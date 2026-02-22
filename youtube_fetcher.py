import yt_dlp
import os
import uuid

def download_youtube(url):
    # Create folders
    os.makedirs("uploads", exist_ok=True)

    # Unique filename
    unique_id = str(uuid.uuid4())
    output_path = f"uploads/{unique_id}.webm"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        "source_address": "0.0.0.0", # Bind to ipv4
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return output_path

    except Exception as e:
        raise Exception(f"Failed to download YouTube video: {str(e)}")
