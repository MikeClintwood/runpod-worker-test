import runpod

def handler(event):
    return {
        "status": "ok",
        "input": event
    }

runpod.serverless.start({"handler": handler})
