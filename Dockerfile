# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=1

# Install system dependencies required by demucs and ffmpeg-python
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install any necessary dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories and set permissions so the app can write to them
RUN mkdir -p /app/uploads /app/separated /app/results /app/output /app/temp && \
    chmod -R 777 /app/uploads /app/separated /app/results /app/output /app/temp

# Copy the rest of the application code
COPY . .

# Ensure permissions are correct after copying local files
RUN chmod -R 777 /app/uploads /app/separated /app/results /app/output /app/temp || true

# Expose the port that the app runs on
EXPOSE 7860

# Run the web service on container startup using gunicorn.
# Hugging Face Spaces default port is 7860
CMD exec gunicorn --bind 0.0.0.0:7860 --workers 1 --threads 8 --timeout 0 app:app
