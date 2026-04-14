import runpod

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

    return {
        "status": "ok",
        "message": "Input received",
        "image_url": image_url,
        "prompt": prompt,
        "format": video_format,
        "duration_seconds": duration_seconds,
        "fps": fps,
        "target_frames": target_frames,
        "target_width": width,
        "target_height": height
    }

runpod.serverless.start({"handler": handler})
