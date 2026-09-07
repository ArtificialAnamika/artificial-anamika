"""Hardware & Sensor Tools for Android / Termux."""

import json
from typing import Dict, Any
from anamika.tools.base import run_command


def get_battery_status() -> Dict[str, Any]:
    """Get the Android device battery status including percentage, health, temperature, and charging state."""
    res = run_command(["termux-battery-status"])
    if res["success"] and res["stdout"]:
        try:
            return json.loads(res["stdout"])
        except Exception:
            return {"raw_output": res["stdout"]}
    return {
        "status": "error",
        "message": res["stderr"] or "Failed to read battery. Ensure Termux:API app is installed."
    }


def set_torch(state: str) -> Dict[str, Any]:
    """Turn the Android flashlight/torch ON or OFF. State must be 'on' or 'off'."""
    clean_state = state.strip().lower()
    if clean_state not in ("on", "off"):
        return {"error": "Invalid state. Use 'on' or 'off'."}
    
    res = run_command(["termux-torch", clean_state])
    if res["success"]:
        return {"status": "success", "torch": clean_state, "message": f"Torch turned {clean_state.upper()}"}
    return {"status": "error", "message": res["stderr"]}


def vibrate(duration_ms: int = 500) -> Dict[str, Any]:
    """Vibrate the phone for a specified duration in milliseconds (default: 500ms)."""
    res = run_command(["termux-vibrate", "-d", str(duration_ms)])
    if res["success"]:
        return {"status": "success", "message": f"Vibrated for {duration_ms}ms"}
    return {"status": "error", "message": res["stderr"]}


def set_brightness(value: int) -> Dict[str, Any]:
    """Set screen brightness value between 0 (dimmest) and 255 (maximum brightness), or auto."""
    val = max(0, min(255, int(value)))
    res = run_command(["termux-brightness", str(val)])
    if res["success"]:
        return {"status": "success", "brightness": val, "message": f"Brightness set to {val}/255"}
    return {"status": "error", "message": res["stderr"]}


def set_volume(stream: str = "music", volume: int = 10) -> Dict[str, Any]:
    """Set volume for a specific audio stream. Stream options: 'music', 'ring', 'notification', 'system', 'call', 'alarm'."""
    stream_clean = stream.strip().lower()
    res = run_command(["termux-volume", stream_clean, str(volume)])
    if res["success"]:
        return {"status": "success", "stream": stream_clean, "volume": volume}
    return {"status": "error", "message": res["stderr"]}


def get_wifi_info() -> Dict[str, Any]:
    """Get current WiFi connection details including SSID, BSSID, IP address, link speed, and state."""
    res = run_command(["termux-wifi-connectioninfo"])
    if res["success"] and res["stdout"]:
        try:
            return json.loads(res["stdout"])
        except Exception:
            return {"raw_output": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}


def get_location(provider: str = "network") -> Dict[str, Any]:
    """Get current GPS/network location (latitude, longitude, altitude, accuracy). Provider can be 'network' or 'gps'."""
    res = run_command(["termux-location", "-p", provider, "-r", "last"], timeout=20)
    if res["success"] and res["stdout"]:
        try:
            return json.loads(res["stdout"])
        except Exception:
            return {"raw_output": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}


def get_sensor_data(sensor: str = "all") -> Dict[str, Any]:
    """Read sensor data such as ambient light, accelerometer, step counter, temperature. Sensor can be 'all', 'light', 'accelerometer', etc."""
    cmd = ["termux-sensor", "-n", "1"]
    if sensor != "all":
        cmd.extend(["-s", sensor])
    res = run_command(cmd, timeout=10)
    if res["success"] and res["stdout"]:
        try:
            return json.loads(res["stdout"])
        except Exception:
            return {"raw_output": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}
