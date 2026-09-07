"""Hardware & Sensor Tools for Android / Termux."""

import json
from typing import Dict, Any, Union
from anamika.tools.base import run_command

VALID_VOLUME_STREAMS = ("music", "ring", "notification", "system", "call", "alarm")


def get_battery_status() -> Dict[str, Any]:
    """Get the Android device battery status including percentage, health, temperature, and charging state."""
    res = run_command(["termux-battery-status"], timeout=10)
    if res["success"] and res["stdout"]:
        try:
            return json.loads(res["stdout"])
        except Exception:
            return {"raw_output": res["stdout"]}
    return {
        "status": "error",
        "message": res["stderr"] or "Failed to read battery. Ensure Termux:API app is installed."
    }


def set_torch(state: Union[str, bool, int] = "on") -> Dict[str, Any]:
    """Turn the Android flashlight/torch ON or OFF. State can be 'on', 'off', True, False, 1, 0."""
    if isinstance(state, bool):
        clean_state = "on" if state else "off"
    else:
        st_str = str(state).strip().lower()
        if st_str in ("on", "1", "true", "enable", "open"):
            clean_state = "on"
        elif st_str in ("off", "0", "false", "disable", "close"):
            clean_state = "off"
        else:
            return {"error": f"Invalid state '{state}'. Use 'on' or 'off'."}
    
    res = run_command(["termux-torch", clean_state], timeout=10)
    if res["success"]:
        return {"status": "success", "torch": clean_state, "message": f"Torch turned {clean_state.upper()}"}
    return {
        "status": "error",
        "message": res["stderr"] or "Failed to toggle torch. Ensure Camera permission is granted to Termux:API app."
    }


def vibrate(duration_ms: Union[int, str] = 500) -> Dict[str, Any]:
    """Vibrate the phone for a specified duration in milliseconds (default: 500ms)."""
    try:
        dur = max(50, min(5000, int(float(str(duration_ms)))))
    except Exception:
        dur = 500

    res = run_command(["termux-vibrate", "-d", str(dur)], timeout=10)
    if res["success"]:
        return {"status": "success", "message": f"Vibrated for {dur}ms"}
    return {"status": "error", "message": res["stderr"]}


def set_brightness(value: Union[int, str] = 128) -> Dict[str, Any]:
    """Set screen brightness value between 0 (dimmest) and 255 (maximum brightness), or 'auto'."""
    val_str = str(value).strip().lower()
    if val_str == "auto":
        res = run_command(["termux-brightness", "auto"], timeout=10)
        if res["success"]:
            return {"status": "success", "brightness": "auto", "message": "Brightness set to AUTO"}
        return {"status": "error", "message": res["stderr"]}
    
    try:
        val = max(0, min(255, int(float(val_str))))
    except Exception:
        val = 128

    res = run_command(["termux-brightness", str(val)], timeout=10)
    if res["success"]:
        return {"status": "success", "brightness": val, "message": f"Brightness set to {val}/255"}
    return {"status": "error", "message": res["stderr"]}


def set_volume(stream: str = "music", volume: Union[int, str] = 10) -> Dict[str, Any]:
    """Set volume for a specific audio stream. Stream options: 'music', 'ring', 'notification', 'system', 'call', 'alarm'."""
    stream_clean = str(stream).strip().lower()
    if stream_clean not in VALID_VOLUME_STREAMS:
        stream_clean = "music"

    try:
        vol = max(0, min(100, int(float(str(volume)))))
    except Exception:
        vol = 10

    res = run_command(["termux-volume", stream_clean, str(vol)], timeout=10)
    if res["success"]:
        return {"status": "success", "stream": stream_clean, "volume": vol}
    return {"status": "error", "message": res["stderr"]}


def get_wifi_info() -> Dict[str, Any]:
    """Get current WiFi connection details including SSID, BSSID, IP address, link speed, and state."""
    res = run_command(["termux-wifi-connectioninfo"], timeout=10)
    if res["success"] and res["stdout"]:
        try:
            return json.loads(res["stdout"])
        except Exception:
            return {"raw_output": res["stdout"]}
    return {
        "status": "error",
        "message": res["stderr"] or "Failed to get WiFi info. Ensure Location permission is granted to Termux:API."
    }


def get_location(provider: str = "network") -> Dict[str, Any]:
    """Get current GPS/network location (latitude, longitude, altitude, accuracy). Provider can be 'network' or 'gps'."""
    prov = "gps" if "gps" in str(provider).lower() else "network"
    res = run_command(["termux-location", "-p", prov, "-r", "last"], timeout=12)
    
    if res["success"] and res["stdout"]:
        try:
            return json.loads(res["stdout"])
        except Exception:
            return {"raw_output": res["stdout"]}
            
    # Fallback to once
    res_fallback = run_command(["termux-location", "-p", prov, "-r", "once"], timeout=10)
    if res_fallback["success"] and res_fallback["stdout"]:
        try:
            return json.loads(res_fallback["stdout"])
        except Exception:
            return {"raw_output": res_fallback["stdout"]}

    return {
        "status": "error",
        "message": res["stderr"] or "Location request timed out. Ensure Location / GPS is turned ON and permission is granted."
    }


def get_sensor_data(sensor: str = "all") -> Dict[str, Any]:
    """Read sensor data such as ambient light, accelerometer, step counter, temperature. Sensor can be 'all', 'light', 'accelerometer', etc."""
    cmd = ["termux-sensor", "-n", "1"]
    if sensor and str(sensor).lower() != "all":
        cmd.extend(["-s", str(sensor).lower()])
    
    res = run_command(cmd, timeout=8)
    
    # Always cleanup / release sensor listener to save battery
    run_command(["termux-sensor", "-c"], timeout=5)
    
    if res["success"] and res["stdout"]:
        try:
            return json.loads(res["stdout"])
        except Exception:
            return {"raw_output": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}
