import runpod

def handler(job):
    job_input = job.get("input", {})

    print("Job erhalten:", job_input)

    return {
        "status": "ok",
        "message": "Worker läuft",
        "input_received": job_input
    }

runpod.serverless.start({"handler": handler})
