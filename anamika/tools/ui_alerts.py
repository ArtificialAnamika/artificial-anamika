"""UI, Notifications, Speech (TTS), Clipboard & Dialog Tools for Android / Termux."""

import json
from typing import Dict, Any
from anamika.tools.base import run_command


def tts_speak(text: str, pitch: float = 1.0, rate: float = 1.0) -> Dict[str, Any]:
    """Speak text aloud using Android's native Text-to-Speech (TTS) engine through device speakers."""
    clean_text = text.strip()
    cmd = ["termux-tts-speak", "-p", str(pitch), "-r", str(rate), clean_text]
    res = run_command(cmd, timeout=30)
    if res["success"]:
        return {"status": "success", "spoken_text": clean_text}
    return {"status": "error", "message": res["stderr"]}


def show_toast(text: str, short: bool = True) -> Dict[str, Any]:
    """Display a popup Toast message on the Android screen."""
    cmd = ["termux-toast"]
    if short:
        cmd.append("-s")
    cmd.append(text)
    res = run_command(cmd, timeout=10)
    if res["success"]:
        return {"status": "success", "toast": text}
    return {"status": "error", "message": res["stderr"]}


def show_notification(title: str, content: str, notification_id: str = "anamika_alert", priority: str = "high") -> Dict[str, Any]:
    """Create a high-priority system status bar notification on Android."""
    cmd = [
        "termux-notification",
        "-t", title,
        "-c", content,
        "-i", notification_id,
        "--priority", priority
    ]
    res = run_command(cmd, timeout=10)
    if res["success"]:
        return {"status": "success", "title": title, "content": content}
    return {"status": "error", "message": res["stderr"]}


def get_clipboard() -> Dict[str, Any]:
    """Get the current text copied to the Android system clipboard."""
    res = run_command(["termux-clipboard-get"], timeout=10)
    if res["success"]:
        return {"status": "success", "clipboard_content": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}


def set_clipboard(text: str) -> Dict[str, Any]:
    """Copy text to the Android system clipboard."""
    res = run_command(["termux-clipboard-set", text], timeout=10)
    if res["success"]:
        return {"status": "success", "message": "Clipboard updated successfully"}
    return {"status": "error", "message": res["stderr"]}


def show_dialog(title: str = "Anamika Prompt", hint: str = "Enter response") -> Dict[str, Any]:
    """Show an interactive text input popup dialog on the Android screen and wait for user response."""
    cmd = ["termux-dialog", "text", "-t", title, "-i", hint]
    res = run_command(cmd, timeout=60)
    if res["success"] and res["stdout"]:
        try:
            return json.loads(res["stdout"])
        except Exception:
            return {"raw_output": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}
