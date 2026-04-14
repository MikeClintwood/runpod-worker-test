import runpod

def handler(event):
    data = event.get("input", {})
    image_url = data.get("image")

    if not image_url:
        return {
            "status": "error",
            "message": "No image URL provided",
            "received_input": data
        }

    return {
        "status": "ok",
        "message": "Image URL received",
        "image_url": image_url
    }

runpod.serverless.start({"handler": handler})
