 import os
import tempfile
import subprocess
import requests
from PIL import Image

from settings import FORMAT_PRESETS, VIDEO_SETTINGS, NETWORK_SETTINGS


class PipelineError(Exception):
    pass


def generate_video(image_url: str, duration_seconds: int, format_name: str) -> bytes:
    temp_files = []

    try:
        img_path = _download_image(image_url)
        temp_files.append(img_path)

        prepared = _prepare_image(img_path, format_name)
        temp_files.append(prepared)

        video_path = _render_video(prepared, duration_seconds)
        temp_files.append(video_path)

        return _read_bytes(video_path)

    except Exception as e:
        raise PipelineError(str(e))

    finally:
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass


def _download_image(url: str) -> str:
    try:
        r = requests.get(url, timeout=NETWORK_SETTINGS["download_timeout"])
        r.raise_for_status()
    except Exception as e:
        raise PipelineError(f"download failed: {e}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(r.content)
        return tmp.name


def _prepare_image(path: str, format_name: str) -> str:
    preset = FORMAT_PRESETS[format_name]
    w, h = preset["width"], preset["height"]

    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            img = _resize_crop(img, w, h)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                img.save(tmp.name, "PNG")
                return tmp.name

    except Exception as e:
        raise PipelineError(f"image prep failed: {e}")


def _resize_crop(img, tw, th):
    sw, sh = img.size
    sr = sw / sh
    tr = tw / th

    if sr > tr:
        nh = th
        nw = int(nh * sr)
    else:
        nw = tw
        nh = int(nw / sr)

    img = img.resize((nw, nh), Image.LANCZOS)

    left = (nw - tw) // 2
    top = (nh - th) // 2

    return img.crop((left, top, left + tw, top + th))


def _render_video(image_path: str, duration: int) -> str:
    vs = VIDEO_SETTINGS

    out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    out.close()

    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-t", str(duration),
        "-r", str(vs["fps"]),
        "-c:v", vs["codec"],
        "-preset", vs["preset"],
        "-crf", str(vs["crf"]),
        "-pix_fmt", vs["pixel_format"],
        out.name
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        raise PipelineError(result.stderr.decode())

    return out.name


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()
