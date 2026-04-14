import runpod
import requests
import tempfile
import subprocess
import base64
import os

def handler(event):
    data = event.get("input", {})

    image_url = data.get("image")
    duration = int(data.get("duration_seconds", 5))
    fps = int(data.get("fps", 8))

    if not image_url:
        return {"status": "error", "message": "No image provided"}

    # -------------------------
    # Bild herunterladen
    # -------------------------
    img_response = requests.get(image_url)
    if img_response.status_code != 200:
        return {"status": "error", "message": "Image download failed"}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_file:
        img_file.write(img_response.content)
        img_path = img_file.name

    # -------------------------
    # Output Video
    # -------------------------
    output_path = tempfile.mktemp(suffix=".mp4")

    # -------------------------
    # FFmpeg Video erstellen
    # -------------------------
    try:
        subprocess.run([
            "ffmpeg",
            "-loop", "1",
            "-i", img_path,
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-vf", f"fps={fps}",
            output_path
        ], check=True)

    except Exception as e:
        return {
            "status": "error",
            "message": f"FFmpeg failed: {str(e)}"
        }

    # -------------------------
    # Video Base64 zurückgeben
    # -------------------------
    with open(output_path, "rb") as f:
        video_bytes = f.read()

    video_base64 = base64.b64encode(video_bytes).decode("utf-8")

    return {
        "status": "ok",
        "message": "REAL video created",
        "video_base64": video_base64,
        "video_filename": f"job_{os.path.basename(output_path)}"
    }


runpod.serverless.start({"handler": handler})
