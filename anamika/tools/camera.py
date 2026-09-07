"""Camera & Photo Capture Tools for Android / Termux."""

import os
import time
from typing import Dict, Any, Union
from anamika.tools.base import run_command

PHOTO_DIR = os.path.expanduser("~/.anamika/photos")


def take_photo(camera_id: Union[int, str] = 0, output_path: str = "") -> Dict[str, Any]:
    """Capture a photo using the phone camera (camera_id: 0 = back camera, 1 = front camera). Returns saved file path."""
    os.makedirs(PHOTO_DIR, exist_ok=True)
    
    # Robust camera_id parsing
    cam_str = str(camera_id).lower().strip()
    if "front" in cam_str or "selfie" in cam_str or cam_str == "1":
        cam_num = 1
        cam_type = "front"
    else:
        cam_num = 0
        cam_type = "back"

    if not output_path:
        timestamp = int(time.time())
        output_path = os.path.join(PHOTO_DIR, f"anamika_{cam_type}_{timestamp}.jpg")
    else:
        output_path = os.path.abspath(os.path.expanduser(output_path))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = ["termux-camera-photo", "-c", str(cam_num), output_path]
    res = run_command(cmd, timeout=20)
    
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return {
            "status": "success",
            "camera_id": cam_num,
            "camera_type": cam_type,
            "photo_path": output_path,
            "size_bytes": os.path.getsize(output_path),
            "message": f"Photo captured successfully from {cam_type} camera and saved to {output_path}"
        }
        
    return {
        "status": "error",
        "message": res["stderr"] or "Failed to capture photo. Ensure Camera permission is granted to Termux:API app."
    }
