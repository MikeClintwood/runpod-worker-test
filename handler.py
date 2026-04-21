import traceback

import runpod

from pipeline import generate_video
from validators import ValidationError, validate_request


def success_response(result: dict) -> dict:
    return {
        "status": "success",
        "output": result
    }


def error_response(code: str, message: str) -> dict:
    return {
        "status": "error",
        "error": {
            "code": code,
            "message": message
        }
    }


def handler(event: dict) -> dict:
    try:
        job_input = event.get("input", {})

        validated_input = validate_request(job_input)

        result = generate_video(validated_input)

        return success_response(result)

    except ValidationError as e:
        return error_response(e.code, e.message)

    except Exception as e:
        traceback.print_exc()
        return error_response(
            "PIPELINE_FAILED",
            f"Unhandled worker error: {str(e)}"
        )


runpod.serverless.start({"handler": handler}) 
