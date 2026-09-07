"""Telephony, SMS, Call Logs & Contact Tools for Android / Termux."""

import re
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Union
from anamika.tools.base import run_command

CALL_TYPE_MAP = {
    1: "INCOMING 🟢",
    2: "OUTGOING 🔵",
    3: "MISSED 🔴",
    4: "VOICEMAIL 🟡",
    5: "REJECTED 🟠",
    6: "BLOCKED ⛔",
    "1": "INCOMING 🟢",
    "2": "OUTGOING 🔵",
    "3": "MISSED 🔴",
    "4": "VOICEMAIL 🟡",
    "5": "REJECTED 🟠",
    "6": "BLOCKED ⛔"
}


def _format_timestamp(ts_val: Any) -> str:
    """Helper to format epoch timestamps (seconds or milliseconds) into readable string."""
    try:
        ts_float = float(ts_val)
        if ts_float > 1e11:
            ts_float /= 1000.0
        return datetime.fromtimestamp(ts_float).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts_val)


def _format_duration(seconds: Any) -> str:
    """Helper to format call duration into human readable minutes/seconds."""
    try:
        sec = int(seconds)
        if sec < 60:
            return f"{sec}s"
        m, s = divmod(sec, 60)
        return f"{m}m {s}s"
    except Exception:
        return f"{seconds}s"


def list_sms(limit: Union[int, str] = 10, offset: Union[int, str] = 0, query: str = "") -> Dict[str, Any]:
    """List recent SMS messages received on the phone, extract OTP codes, or filter by keyword/sender."""
    try:
        lim = max(1, min(50, int(limit)))
        off = max(0, int(offset))
    except Exception:
        lim, off = 10, 0

    cmd = ["termux-sms-list", "-l", str(lim), "-o", str(off)]
    res = run_command(cmd, timeout=15)
    
    if res["success"] and res["stdout"]:
        try:
            messages = json.loads(res["stdout"])
            parsed = []
            otp_pattern = re.compile(r'\b(?:\d{4,8}|[A-Z0-9]{5,8})\b')
            
            for msg in messages:
                body = msg.get("body", "")
                number = msg.get("number", "")
                received = _format_timestamp(msg.get("received", ""))
                
                # Filter by query if provided
                if query and (query.lower() not in body.lower() and query not in number):
                    continue
                
                # Extract potential OTPs
                potential_otps = []
                if any(w in body.lower() for w in ("otp", "code", "verification", "password", "pin", "login")):
                    matches = otp_pattern.findall(body)
                    potential_otps = [m for m in matches if any(char.isdigit() for char in m)]

                parsed.append({
                    "sender": number,
                    "date": received,
                    "body": body,
                    "read": msg.get("read", False),
                    "potential_otps": potential_otps
                })

            # Build beautiful formatted text for humans & LLM
            formatted_lines = [f"📩 RECENT SMS (Total: {len(parsed)}):", "━" * 40]
            for idx, m in enumerate(parsed, start=1):
                otp_str = f"\n   🔑 OTP Code: {', '.join(m['potential_otps'])}" if m['potential_otps'] else ""
                formatted_lines.append(
                    f"{idx}. 👤 From: {m['sender']}\n"
                    f"   ⏰ Date: {m['date']}{otp_str}\n"
                    f"   💬 Message: {m['body']}\n"
                    + "━" * 40
                )

            formatted_summary = "\n".join(formatted_lines)

            return {
                "status": "success",
                "count": len(parsed),
                "messages": parsed,
                "formatted_text": formatted_summary
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to parse SMS: {e}", "raw": res["stdout"]}

    return {
        "status": "error",
        "message": res["stderr"] or "Failed to list SMS. Ensure SMS permission is granted to Termux:API app."
    }


def send_sms(number: str, message: str) -> Dict[str, Any]:
    """Send an SMS message to a specific phone number."""
    clean_num = str(number).strip().replace(" ", "").replace("-", "")
    res = run_command(["termux-sms-send", "-n", clean_num, str(message)], timeout=15)
    if res["success"]:
        return {"status": "success", "recipient": clean_num, "message": "SMS sent successfully"}
    return {
        "status": "error",
        "message": res["stderr"] or "Failed to send SMS. Ensure SMS permission is granted to Termux:API app."
    }


def get_call_logs(limit: Union[int, str] = 10, offset: Union[int, str] = 0) -> Dict[str, Any]:
    """View recent incoming, outgoing, and missed call logs with caller details and timestamps."""
    try:
        lim = max(1, min(50, int(limit)))
        off = max(0, int(offset))
    except Exception:
        lim, off = 10, 0

    # 1. Primary Method: termux-telephony-call-log
    cmd = ["termux-telephony-call-log", "-l", str(lim), "-o", str(off)]
    res = run_command(cmd, timeout=15)
    
    raw_calls = []
    if res["success"] and res["stdout"]:
        try:
            parsed_json = json.loads(res["stdout"])
            if isinstance(parsed_json, list) and len(parsed_json) > 0:
                raw_calls = parsed_json
        except Exception:
            pass

    formatted_calls = []

    if raw_calls:
        for c in raw_calls:
            raw_type = c.get("type", "")
            readable_type = CALL_TYPE_MAP.get(raw_type, str(raw_type))
            formatted_calls.append({
                "name": c.get("name") or "Unknown / Unsaved",
                "phone_number": c.get("phone_number") or c.get("number", ""),
                "type": readable_type,
                "date": _format_timestamp(c.get("date", "")),
                "duration": _format_duration(c.get("duration", 0))
            })
    else:
        # 2. Fallback Method: Direct Android Content Provider Query
        content_cmd = [
            "content", "query",
            "--uri", "content://call_log/calls",
            "--projection", "number:name:date:duration:type",
            "--sort", "date DESC"
        ]
        res_content = run_command(content_cmd, timeout=10)
        if res_content["success"] and res_content["stdout"]:
            lines = res_content["stdout"].splitlines()
            for line in lines[:lim]:
                if "Row:" in line:
                    item = {}
                    for part in line.split(","):
                        if "=" in part:
                            k, v = part.split("=", 1)
                            item[k.strip().replace("Row: ", "")] = v.strip()
                    
                    raw_type = item.get("type", "1")
                    formatted_calls.append({
                        "name": item.get("name") or "Unknown / Unsaved",
                        "phone_number": item.get("number", ""),
                        "type": CALL_TYPE_MAP.get(raw_type, "CALL"),
                        "date": _format_timestamp(item.get("date", "")),
                        "duration": _format_duration(item.get("duration", 0))
                    })

    if formatted_calls:
        # Build formatted summary
        formatted_lines = [f"📞 RECENT CALL LOGS (Total: {len(formatted_calls)}):", "━" * 40]
        for idx, c in enumerate(formatted_calls, start=1):
            formatted_lines.append(
                f"{idx}. 👤 {c['name']} ({c['phone_number']})\n"
                f"   📞 {c['type']} | ⏱️ {c['duration']}\n"
                f"   ⏰ {c['date']}\n"
                + "━" * 40
            )

        return {
            "status": "success",
            "count": len(formatted_calls),
            "calls": formatted_calls,
            "formatted_text": "\n".join(formatted_lines)
        }

    return {
        "status": "success",
        "count": 0,
        "calls": [],
        "message": "No call logs found on this device. (Ensure Call Logs & Phone permissions are granted to Termux:API app)."
    }


def list_contacts(query: str = "") -> Dict[str, Any]:
    """Search phonebook contacts by name or phone number."""
    res = run_command(["termux-contact-list"], timeout=15)
    if res["success"] and res["stdout"]:
        try:
            contacts = json.loads(res["stdout"])
            if query:
                q_low = str(query).lower()
                contacts = [c for c in contacts if q_low in str(c.get("name", "")).lower() or q_low in str(c.get("number", ""))]
            return {
                "status": "success",
                "count": len(contacts),
                "contacts": contacts[:30]
            }
        except Exception:
            return {"raw_output": res["stdout"]}
    return {
        "status": "error",
        "message": res["stderr"] or "Failed to read contacts. Ensure Contacts permission is granted to Termux:API app."
    }


def get_cell_info() -> Dict[str, Any]:
    """Get SIM card details, mobile carrier network type, and signal information."""
    res = run_command(["termux-telephony-cellinfo"], timeout=15)
    if res["success"] and res["stdout"]:
        try:
            return {"status": "success", "cell_info": json.loads(res["stdout"])}
        except Exception:
            return {"raw_output": res["stdout"]}
    return {
        "status": "error",
        "message": res["stderr"] or "Failed to read cellular info. (Device might be WiFi-only tablet or SIM not present)."
    }
