"""Camera & Photo Capture Tools for Android / Termux."""

import os
import time
from typing import Dict, Any
from anamika.tools.base import run_command

PHOTO_DIR = os.path.expanduser("~/.anamika/photos")


def take_photo(camera_id: int = 0, output_path: str = "") -> Dict[str, Any]:
    """Capture a photo using the phone camera (camera_id: 0 = back camera, 1 = front camera). Returns saved file path."""
    os.makedirs(PHOTO_DIR, exist_ok=True)
    
    if not output_path:
        timestamp = int(time.time())
        cam_type = "front" if int(camera_id) == 1 else "back"
        output_path = os.path.join(PHOTO_DIR, f"anamika_{cam_type}_{timestamp}.jpg")
    else:
        output_path = os.path.abspath(os.path.expanduser(output_path))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = ["termux-camera-photo", "-c", str(camera_id), output_path]
    res = run_command(cmd, timeout=20)
    
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return {
            "status": "success",
            "camera_id": camera_id,
            "photo_path": output_path,
            "size_bytes": os.path.getsize(output_path),
            "message": f"Photo captured successfully and saved to {output_path}"
        }
        
    return {
        "status": "error",
        "message": res["stderr"] or "Failed to capture photo. Ensure Termux:API camera permission is granted."
    }
