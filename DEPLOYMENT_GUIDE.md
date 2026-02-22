# How to Deploy VocalX Web

VocalX relies on heavy AI libraries (`torch`, `demucs`) and external system tools (`ffmpeg`). For this reason, standard free Python script hosting platforms (like PythonAnywhere, Heroku free tier, or Render free tier) will either run out of memory or fail because they lack `ffmpeg`.

The **best free option** for hosting this application is **Hugging Face Spaces**. Hugging Face provides a generous 16GB of RAM and allows running Docker containers, which we need to install `ffmpeg`.

## Deployment Steps (Hugging Face Spaces)

1. **Create a Hugging Face Account**: 
   Go to [huggingface.co](https://huggingface.co/) and sign up.

2. **Create a New Space**:
   - Go to your profile -> Spaces -> **Create new Space**.
   - **Space Name**: Choose a name (e.g., `vocalx-web`).
   - **License**: Choose your preferred license (e.g., MIT).
   - **Select the Space SDK**: Choose **Docker**.
   - **Choose a Docker template**: Select **Blank**.
   - Click **Create Space**.

3. **Upload Your Files**:
   Your space is essentially a Git repository. You have two ways to add your code:

   **Method A: Browser Upload (Easiest)**
   - On your Space page, go to the **Files** tab.
   - Click **Add file** -> **Upload files**.
   - Drag and drop ALL the files in your project directory (including `app.py`, `requirements.txt`, `Dockerfile`, `.dockerignore`, and the `templates` and `static` folders).
   - **Do not** upload the `uploads`, `separated`, `temp`, `output`, or `results` folders (the `.dockerignore` file helps prevent this if using git, but if uploading manually, just skip them).
   - Commit the changes.

   **Method B: Git Terminal (Recommended for Developers)**
   - Clone the huggingface space repository to a new folder:
     ```bash
     git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
     ```
   - Copy all your VocalX Web project files into that cloned folder.
   - Commit and push to Hugging Face:
     ```bash
     git add .
     git commit -m "Initial commit for VocalX deploy"
     git push
     ```

4. **Watch it Build**:
   Once the files are uploaded, Hugging Face will automatically detect the `Dockerfile` and start building the container.
   - You can click on the **Logs** button to see the build progress. 
   - It will install Linux dependencies (`ffmpeg`) and Pip dependencies (`demucs`, `flask`, `torch`, etc.). This might take a few minutes.

5. **App is Live!**
   Once the build completes and it says "Running", your app will be accessible online via the public Hugging Face Space URL.

## Important Notes on Production Deployment
- **Port**: Hugging Face Spaces exposes port `7860` by default. The provided `Dockerfile` is already configured to start the `gunicorn` server on `0.0.0.0:7860`.
- **Temp Files Storage**: The uploaded tracks and separated files eat up disk space quickly. The app currently cleans up temporary folders correctly inside `app.py`, which is perfect for cloud deployment where disk space is limited.
- **Memory Management**: `demucs` uses an extensive amount of RAM to load the AI models into memory. Hugging Face's 16GB limit should be enough for single-file track separations, but concurrent users submitting large files may bottleneck the processing. The `Dockerfile` sets Gunicorn to `workers 1` specifically to prevent multiple processes from crashing the server due to Memory constraints.
