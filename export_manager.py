# export_manager.py
import ffmpeg
from pydub import AudioSegment
import os
import zipfile
import shutil

EXPORT_DIR = "output"
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_outputs(vocals, instrumental, cleaned_vocals, output_type, original_video):
    uid = os.path.basename(os.path.dirname(vocals))

    mp3_out = f"{EXPORT_DIR}/{uid}_vocals.mp3"
    wav_out = f"{EXPORT_DIR}/{uid}_vocals.wav"
    mp4_vocals_out = f"{EXPORT_DIR}/{uid}_video_clean_vocals.mp4"
    mp4_instru_out = f"{EXPORT_DIR}/{uid}_video_instrumental.mp4"

    # MP3
    if output_type == "mp3":
        AudioSegment.from_wav(cleaned_vocals).export(mp3_out, format="mp3")
        return {"file": mp3_out}

    # WAV
    if output_type == "wav":
        AudioSegment.from_wav(cleaned_vocals).export(wav_out, format="wav")
        return {"file": wav_out}

    # MP4 with original video + cleaned vocals
    if output_type == "mp4_vocals":
        (
            ffmpeg.input(original_video)
            .output(cleaned_vocals, mp4_vocals_out, vcodec="copy", acodec="aac", strict="-2")
            .overwrite_output()
            .run(quiet=True)
        )
        return {"file": mp4_vocals_out}

    # MP4 with instrumental only
    if output_type == "mp4_instrumental":
        (
            ffmpeg.input(original_video)
            .output(instrumental, mp4_instru_out, vcodec="copy", acodec="aac", strict="-2")
            .overwrite_output()
            .run(quiet=True)
        )
        return {"file": mp4_instru_out}

    # STEM PACK (vocals + instrumental)
    if output_type == "stems":
        zip_path = f"{EXPORT_DIR}/{uid}_stems.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(vocals, arcname="vocals.wav")
            zipf.write(instrumental, arcname="instrumental.wav")
        return {"file": zip_path}

    # ALL OUTPUTS IN ZIP
    if output_type == "zip_all":
        zip_path = f"{EXPORT_DIR}/{uid}_all_outputs.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(cleaned_vocals, arcname="cleaned_vocals.wav")
            zipf.write(vocals, arcname="raw_vocals.wav")
            zipf.write(instrumental, arcname="instrumental.wav")
        return {"file": zip_path}

    return {"error": "Unknown output type"}
