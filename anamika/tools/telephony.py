"""Telephony, SMS, Call Logs & Contact Tools for Android / Termux."""

import re
import json
from typing import Dict, Any, List
from anamika.tools.base import run_command


def list_sms(limit: int = 10, offset: int = 0, query: str = "") -> Dict[str, Any]:
    """List recent SMS messages received on the phone, extract OTP codes, or filter by keyword/sender."""
    cmd = ["termux-sms-list", "-l", str(limit), "-o", str(offset)]
    res = run_command(cmd, timeout=15)
    
    if res["success"] and res["stdout"]:
        try:
            messages = json.loads(res["stdout"])
            parsed = []
            otp_pattern = re.compile(r'\b(?:\d{4,8}|[A-Z0-9]{5,8})\b')
            
            for msg in messages:
                body = msg.get("body", "")
                number = msg.get("number", "")
                received = msg.get("received", "")
                
                # Filter by query if provided
                if query and (query.lower() not in body.lower() and query not in number):
                    continue
                
                # Try finding potential OTP in body
                potential_otps = []
                if "otp" in body.lower() or "code" in body.lower() or "verification" in body.lower() or "password" in body.lower():
                    matches = otp_pattern.findall(body)
                    potential_otps = [m for m in matches if any(char.isdigit() for char in m)]

                parsed.append({
                    "sender": number,
                    "received": received,
                    "body": body,
                    "read": msg.get("read", False),
                    "potential_otps": potential_otps
                })

            return {
                "status": "success",
                "count": len(parsed),
                "messages": parsed
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to parse SMS: {e}", "raw": res["stdout"]}

    return {"status": "error", "message": res["stderr"] or "Failed to list SMS"}


def send_sms(number: str, message: str) -> Dict[str, Any]:
    """Send an SMS message to a specific phone number."""
    clean_num = number.strip().replace(" ", "").replace("-", "")
    res = run_command(["termux-sms-send", "-n", clean_num, message], timeout=15)
    if res["success"]:
        return {"status": "success", "recipient": clean_num, "message": "SMS sent successfully"}
    return {"status": "error", "message": res["stderr"]}


def get_call_logs(limit: int = 10, offset: int = 0) -> Dict[str, Any]:
    """View recent incoming, outgoing, and missed call logs."""
    cmd = ["termux-telephony-call-log", "-l", str(limit), "-o", str(offset)]
    res = run_command(cmd, timeout=15)
    if res["success"] and res["stdout"]:
        try:
            return {
                "status": "success",
                "calls": json.loads(res["stdout"])
            }
        except Exception:
            return {"raw_output": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}


def list_contacts(query: str = "") -> Dict[str, Any]:
    """Search phonebook contacts by name or phone number."""
    res = run_command(["termux-contact-list"], timeout=15)
    if res["success"] and res["stdout"]:
        try:
            contacts = json.loads(res["stdout"])
            if query:
                q_low = query.lower()
                contacts = [c for c in contacts if q_low in c.get("name", "").lower() or q_low in c.get("number", "")]
            return {
                "status": "success",
                "count": len(contacts),
                "contacts": contacts[:30]
            }
        except Exception:
            return {"raw_output": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}


def get_cell_info() -> Dict[str, Any]:
    """Get SIM card details, mobile carrier network type, and signal information."""
    res = run_command(["termux-telephony-cellinfo"], timeout=15)
    if res["success"] and res["stdout"]:
        try:
            return {"status": "success", "cell_info": json.loads(res["stdout"])}
        except Exception:
            return {"raw_output": res["stdout"]}
    return {"status": "error", "message": res["stderr"]}
