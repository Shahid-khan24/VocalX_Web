# demucs_runner.py
import subprocess
import os
import uuid
from pathlib import Path
import shutil

UPLOAD_DIR = "uploads"
SEPARATED_DIR = "separated/htdemucs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SEPARATED_DIR, exist_ok=True)

def separate_stems(original_path):
    # Create a temporary clean filename
    uid = str(uuid.uuid4())
    temp_wav = f"{UPLOAD_DIR}/{uid}.wav"

    # Convert ANY uploaded file to WAV for Demucs
    subprocess.run(
        ["ffmpeg", "-y", "-i", original_path, "-ac", "2", "-ar", "44100", temp_wav],
        capture_output=True, text=True
    )

    # After conversion, delete the raw upload immediately
    if os.path.exists(original_path):
        os.remove(original_path)

    # Run Demucs
    cmd = ["demucs", "--two-stems=vocals", temp_wav]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Demucs failed:\n{result.stderr}")

    # Output folder (Demucs always names by stem)
    out_folder = f"{SEPARATED_DIR}/{uid}"
    vocals = f"{out_folder}/vocals.wav"
    instrumental = f"{out_folder}/accompaniment.wav"

    if not os.path.exists(vocals):
        raise FileNotFoundError("Demucs did not produce vocals.wav")

    if not os.path.exists(instrumental):
        raise FileNotFoundError("Demucs did not produce accompaniment.wav")

    # Remove the temp wav after separation
    if os.path.exists(temp_wav):
        os.remove(temp_wav)

    return {
        "uid": uid,
        "vocals": vocals,
        "instrumental": instrumental
    }
