"""Android OS Intents, App Launching, Settings & Media Tools."""

import subprocess
from typing import Dict, Any
from anamika.tools.base import run_command

APP_PACKAGES = {
    "whatsapp": "com.whatsapp",
    "whatsapp_business": "com.whatsapp.w4b",
    "youtube": "com.google.android.youtube",
    "chrome": "com.android.chrome",
    "settings": "com.android.settings",
    "telegram": "org.telegram.messenger",
    "termux": "com.termux",
    "maps": "com.google.android.apps.maps",
    "gallery": "com.google.android.apps.photos",
    "photos": "com.google.android.apps.photos",
    "playstore": "com.android.vending",
    "play_store": "com.android.vending",
    "gmail": "com.google.android.gm",
    "macrodroid": "com.arlosoft.macrodroid",
    "files": "com.google.android.documentsui",
    "camera": "android.hardware.camera2"
}

SETTINGS_INTENTS = {
    "main": "android.settings.SETTINGS",
    "wifi": "android.settings.WIFI_SETTINGS",
    "bluetooth": "android.settings.BLUETOOTH_SETTINGS",
    "battery": "android.settings.BATTERY_SAVER_SETTINGS",
    "display": "android.settings.DISPLAY_SETTINGS",
    "location": "android.settings.LOCATION_SOURCE_SETTINGS",
    "apps": "android.settings.APPLICATION_SETTINGS",
    "sound": "android.settings.SOUND_SETTINGS",
    "date": "android.settings.DATE_SETTINGS"
}


def launch_app(app_name: str, package_name: str = "") -> Dict[str, Any]:
    """Launch an Android application by name (e.g. 'whatsapp', 'youtube', 'chrome', 'settings', 'telegram') or package name."""
    pkg = package_name.strip()
    clean_name = app_name.strip().lower().replace(" ", "_")
    
    if not pkg:
        pkg = APP_PACKAGES.get(clean_name, app_name.strip())

    # Try monkey command first (most reliable on Android for launching main intent)
    cmd = ["monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"]
    res = run_command(cmd, timeout=10)
    
    if res["success"]:
        return {"status": "success", "package": pkg, "message": f"Launched {app_name} ({pkg})"}
    
    # Fallback to am start
    res_am = run_command(["am", "start", "-n", f"{pkg}/.MainActivity"], timeout=10)
    if res_am["success"]:
        return {"status": "success", "package": pkg, "message": f"Started {pkg}"}
        
    return {
        "status": "error",
        "package": pkg,
        "message": f"Failed to launch app. Error: {res['stderr'] or res_am['stderr']}"
    }


def open_url(url: str) -> Dict[str, Any]:
    """Open a web URL in the Android default web browser."""
    clean_url = url.strip()
    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = "https://" + clean_url
        
    res = run_command(["termux-open-url", clean_url], timeout=10)
    if res["success"]:
        return {"status": "success", "url": clean_url, "message": "Opened URL in browser"}
        
    # Fallback to Android intent
    res_am = run_command(["am", "start", "-a", "android.intent.action.VIEW", "-d", clean_url], timeout=10)
    if res_am["success"]:
        return {"status": "success", "url": clean_url}
        
    return {"status": "error", "message": res["stderr"] or res_am["stderr"]}


def open_settings(setting_type: str = "main") -> Dict[str, Any]:
    """Open specific Android Settings screen ('main', 'wifi', 'bluetooth', 'battery', 'display', 'location', 'apps', 'sound')."""
    intent_action = SETTINGS_INTENTS.get(setting_type.lower().strip(), "android.settings.SETTINGS")
    res = run_command(["am", "start", "-a", intent_action], timeout=10)
    if res["success"]:
        return {"status": "success", "setting_type": setting_type, "intent": intent_action}
    return {"status": "error", "message": res["stderr"]}


def play_media(file_path: str, action: str = "play") -> Dict[str, Any]:
    """Play, pause, stop or get info on local audio files using Android media player. Action: 'play', 'pause', 'stop', 'info'."""
    act = action.strip().lower()
    cmd = ["termux-media-player", act]
    if act == "play" and file_path:
        cmd.append(file_path)
    res = run_command(cmd, timeout=15)
    if res["success"]:
        return {"status": "success", "action": act, "output": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}


def download_file(url: str, description: str = "Anamika Download") -> Dict[str, Any]:
    """Download a file in the background using native Android Download Manager."""
    cmd = ["termux-download", "-d", description, url]
    res = run_command(cmd, timeout=15)
    if res["success"]:
        return {"status": "success", "url": url, "message": "Download initiated in Android Download Manager"}
    return {"status": "error", "message": res["stderr"]}
