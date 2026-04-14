import os
import subprocess
import uuid

import requests
import runpod


def download_image(image_url: str, output_path: str) -> None:
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)


def build_video_from_image(
    image_path: str,
    output_path: str,
    width: int,
    height: int,
    duration_seconds: int,
    fps: int,
) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-t", str(duration_seconds),
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        "-r", str(fps),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")


def handler(event):
    data = event.get("input", {})

    image_url = data.get("image")
    prompt = data.get("prompt", "")
    video_format = data.get("format", "vertical")
    duration_seconds = int(data.get("duration_seconds", 5))

    if not image_url:
        return {
            "status": "error",
            "message": "No image URL provided",
            "received_input": data
        }

    if video_format not in ["vertical", "horizontal"]:
        video_format = "vertical"

    if duration_seconds not in [3, 5, 8, 10]:
        duration_seconds = 5

    if video_format == "vertical":
        width, height = 720, 1280
    else:
        width, height = 1280, 720

    fps = 8
    target_frames = duration_seconds * fps

    job_id = uuid.uuid4().hex
    image_path = f"/tmp/input_{job_id}.png"
    output_path = f"/tmp/output_{job_id}.mp4"

    try:
        download_image(image_url, image_path)
        build_video_from_image(
            image_path=image_path,
            output_path=output_path,
            width=width,
            height=height,
            duration_seconds=duration_seconds,
            fps=fps,
        )

        if not os.path.exists(output_path):
            return {
                "status": "error",
                "message": "Video file was not created"
            }

        video_size = os.path.getsize(output_path)

        return {
            "status": "ok",
            "message": "Dummy video created successfully",
            "image_url": image_url,
            "prompt": prompt,
            "format": video_format,
            "duration_seconds": duration_seconds,
            "fps": fps,
            "target_frames": target_frames,
            "target_width": width,
            "target_height": height,
            "video_path": output_path,
            "video_size_bytes": video_size
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "image_url": image_url
        }

    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


runpod.serverless.start({"handler": handler})
