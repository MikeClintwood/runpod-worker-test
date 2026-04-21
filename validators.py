ALLOWED_DURATIONS = [3, 5]
ALLOWED_FORMATS = ["portrait", "landscape"]


def validate_input(data: dict):
    if "image_url" not in data:
        raise ValueError("image_url missing")

    if "duration_seconds" not in data:
        raise ValueError("duration_seconds missing")

    if "format" not in data:
        raise ValueError("format missing")

    duration = int(data["duration_seconds"])
    if duration not in ALLOWED_DURATIONS:
        raise ValueError("duration must be 3 or 5")

    fmt = data["format"]
    if fmt not in ALLOWED_FORMATS:
        raise ValueError("format must be portrait or landscape")
