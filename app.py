import os
import uuid
import threading
from flask import Flask, request, jsonify, send_from_directory
from processing_pipeline import process_file
from youtube_fetcher import download_youtube
import shutil

app = Flask(__name__)

# ========= IN-MEMORY JOB STORE =========
jobs = {}  # job_id -> {"status": ..., "result": ..., "error": ...}

# ========= AUTO-CLEAN TEMP FOLDERS =========
def clean_temp():
    folders = ["uploads", "separated", "temp"]
    for f in folders:
        if os.path.exists(f):
            shutil.rmtree(f, ignore_errors=True)

    # Recreate empty folders after cleaning
    for f in folders:
        os.makedirs(f, exist_ok=True)


# ========= IGNORE FAVICON REQUEST =========
@app.route('/favicon.ico')
def favicon():
    return '', 204


# ========= BG WORKER =========
def run_job(job_id, youtube_link, filepath, output_type, pitch_mode, start_time, end_time):
    try:
        jobs[job_id]["status"] = "processing"

        # Download YouTube if needed (heavy - do inside thread)
        if youtube_link:
            filepath = download_youtube(youtube_link)

        output_files = process_file(filepath, output_type, pitch_mode, start_time, end_time)
        outputs = []
        for label, filename in output_files.items():
            outputs.append({"label": label, "url": f"/download/{os.path.basename(filename)}"})
        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = outputs
        clean_temp()
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


# ========= MAIN PROCESSING ENDPOINT =========
@app.route("/process_upload", methods=["POST"])
def process_upload():
    try:
        youtube_link = request.form.get("youtube_link", "").strip()
        pitch_mode = request.form.get("pitch_mode")
        output_type = request.form.get("output_type")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        os.makedirs("uploads", exist_ok=True)
        os.makedirs("output", exist_ok=True)

        filepath = None
        if not (youtube_link and len(youtube_link) > 5):
            # Save uploaded file synchronously (fast - just I/O)
            uploaded = request.files.get("file")
            if not uploaded:
                return jsonify({"error": "No input file or YouTube link provided"}), 400
            save_path = os.path.join("uploads", uploaded.filename)
            uploaded.save(save_path)
            filepath = save_path
            youtube_link = None  # already handled

        # Queue the job - return immediately!
        job_id = str(uuid.uuid4())
        jobs[job_id] = {"status": "queued", "result": None, "error": None}
        t = threading.Thread(
            target=run_job,
            args=(job_id, youtube_link, filepath, output_type, pitch_mode, start_time, end_time),
            daemon=True
        )
        t.start()

        return jsonify({"job_id": job_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========= JOB STATUS ENDPOINT =========
@app.route("/status/<job_id>")
def job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


# ========= DOWNLOAD ENDPOINT =========
@app.route("/download/<path:filename>")
def download_file(filename):
    # export_manager writes to "output/" folder
    for folder in ["output", "results"]:
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath):
            return send_from_directory(folder, filename, as_attachment=True)
    return jsonify({"error": "File not found"}), 404


# ========= HOME PAGE =========
@app.route("/")
def home():
    return send_from_directory("templates", "index.html")


# ========= STATIC FILES (CSS / JS / IMAGES) =========
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


# ========= START SERVER =========
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
