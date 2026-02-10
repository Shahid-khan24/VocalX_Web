import os
from flask import Flask, request, jsonify, send_from_directory
from processing_pipeline import process_file
from youtube_fetcher import download_youtube
import shutil

app = Flask(__name__)

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


# ========= MAIN PROCESSING ENDPOINT =========
@app.route("/process_upload", methods=["POST"])
def process_upload():
    try:
        youtube_link = request.form.get("youtube_link")
        pitch_mode = request.form.get("pitch_mode")
        output_type = request.form.get("output_type")

        # Ensure working folders exist
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("results", exist_ok=True)

        # ====== YOUTUBE MODE ======
        if youtube_link and len(youtube_link.strip()) > 5:
            filepath = download_youtube(youtube_link)
        else:
            # ====== UPLOAD MODE ======
            uploaded = request.files.get("file")
            if not uploaded:
                return jsonify({"error": "No input file provided"}), 400

            save_path = os.path.join("uploads", uploaded.filename)
            uploaded.save(save_path)
            filepath = save_path

        # ====== RUN MAIN VOCALX PROCESSING ======
        output_files = process_file(filepath, output_type, pitch_mode)

        # ====== BUILD JSON RESPONSE ======
        response_data = {
            "status": "success",
            "outputs": []
        }

        for label, filename in output_files.items():
            response_data["outputs"].append({
                "label": label,
                "url": f"/download/{filename}"
            })

        # ====== CLEAN TEMP AFTER PROCESSING ======
        clean_temp()

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========= DOWNLOAD ENDPOINT =========
@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory("results", filename, as_attachment=True)


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
