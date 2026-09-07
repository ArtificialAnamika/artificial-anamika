"""Zero-Dependency 24x7 Telegram Daemon for Artificial Anamika."""

import os
import sys
import json
import ssl
import time
import mimetypes
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional
from anamika.config import Config
from anamika.agent import Agent
from anamika.tools.hardware import get_battery_status, set_torch, get_wifi_info
from anamika.tools.telephony import list_sms, get_call_logs
from anamika.tools.camera import take_photo
from anamika.tools.shell_system import execute_shell


class TelegramBot:
    """Autonomous Telegram Daemon connecting Anant to his Android device via Anamika."""

    def __init__(self, config: Config, agent: Optional[Agent] = None):
        self.config = config
        self.token = config.telegram_token
        self.allowed_users = [int(u) for u in config.allowed_telegram_users if str(u).isdigit()]
        self.agent = agent or Agent(config)
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        self.running = False

    def _request(self, method: str, data: Optional[Dict[str, Any]] = None, timeout: int = 30) -> Dict[str, Any]:
        """Makes an HTTP POST/GET request to Telegram Bot API with error capture."""
        url = f"{self.base_url}/{method}"
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        if data:
            data_bytes = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
        else:
            req = urllib.request.Request(url, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read().decode("utf-8"))
                return err_body
            except Exception:
                return {"ok": False, "error_code": e.code, "description": str(e)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def clear_webhook(self) -> None:
        """Clears any stale webhook so getUpdates long-polling works reliably."""
        res = self._request("deleteWebhook", {"drop_pending_updates": False})
        if res.get("ok"):
            print("✓ Telegram Webhook cleared (Long-polling active)")
        else:
            print(f"ℹ️ Webhook check: {res.get('description', 'OK')}")

    def send_message(self, chat_id: int, text: str, parse_mode: Optional[str] = None) -> Dict[str, Any]:
        """Sends a text message with automatic length splitting and markdown fallback."""
        if not text:
            return {}

        # If text is too long, chunk it
        if len(text) > 4000:
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            last_res = {}
            for chunk in chunks:
                last_res = self._send_single_message(chat_id, chunk, parse_mode)
            return last_res

        return self._send_single_message(chat_id, text, parse_mode)

    def _send_single_message(self, chat_id: int, text: str, parse_mode: Optional[str] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode

        res = self._request("sendMessage", payload)
        
        # If markdown parsing failed on Telegram side, retry immediately as plain text!
        if not res.get("ok") and parse_mode:
            print(f"⚠️ Markdown formatting error ({res.get('description')}). Retrying as plain text...")
            payload.pop("parse_mode", None)
            res = self._request("sendMessage", payload)

        if not res.get("ok"):
            print(f"❌ Failed to send message to {chat_id}: {res.get('description')}")
        return res

    def send_photo(self, chat_id: int, photo_path: str, caption: str = "") -> Dict[str, Any]:
        """Uploads and sends a photo file to Telegram chat."""
        if not os.path.exists(photo_path):
            return self.send_message(chat_id, f"⚠️ Photo file not found: {photo_path}")

        boundary = "----AnamikaBoundary" + str(int(time.time()))
        url = f"{self.base_url}/sendPhoto"

        body = bytearray()
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode("utf-8"))

        if caption:
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode("utf-8"))

        filename = os.path.basename(photo_path)
        mime_type = mimetypes.guess_type(photo_path)[0] or "image/jpeg"
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="photo"; filename="{filename}"\r\n'.encode("utf-8"))
        body.extend(f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"))
        with open(photo_path, "rb") as f:
            body.extend(f.read())
        body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            url,
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=40, context=ctx) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return self.send_message(chat_id, f"⚠️ Failed to upload photo: {e}")

    def send_chat_action(self, chat_id: int, action: str = "typing") -> None:
        """Sends 'typing' or 'upload_photo' action indicator."""
        self._request("sendChatAction", {"chat_id": chat_id, "action": action})

    def handle_message(self, message: Dict[str, Any]) -> None:
        """Processes incoming Telegram message with authentication & routing."""
        chat_id = message.get("chat", {}).get("id")
        user = message.get("from", {})
        user_id = user.get("id")
        username = user.get("username", "") or user.get("first_name", "User")
        text = message.get("text", "").strip()

        if not chat_id or not text:
            return

        print(f"📩 [Telegram Message] ID: {user_id} (@{username}): '{text}'")

        # Security check: Whitelist
        if self.allowed_users and int(user_id) not in self.allowed_users:
            print(f"🔒 Blocked unauthorized access from user_id: {user_id}. Allowed: {self.allowed_users}")
            self.send_message(chat_id, f"⛔ Access Denied. Your Telegram User ID ({user_id}) is not in the whitelist.")
            return

        # Quick Slash Commands
        if text.startswith("/start") or text.startswith("/help"):
            help_text = (
                "✨ Artificial Anamika — Android AI Employee\n\n"
                f"📱 Device: {self.config.device_name}\n"
                f"🧠 Model:  {self.config.model}\n"
                f"⚡ Endpoint: {self.config.endpoint}\n\n"
                "Available Commands:\n"
                "• /status — Device health, battery & WiFi info\n"
                "• /battery — Detailed battery statistics\n"
                "• /torch on|off — Toggle flashlight\n"
                "• /photo — Click photo and send here\n"
                "• /sms — View recent SMS & OTPs\n"
                "• /calls — View recent call logs\n"
                "• /exec <cmd> — Run bash command in Termux\n"
                "• /reset — Clear conversation history\n\n"
                "💡 Natural Language: Aap mujhe seedhe Hinglish me bol sakte hain (e.g. 'Battery check karo', 'Torch on kar do', 'Recent call logs dikhao', 'SMS dikhao', 'WhatsApp kholo')."
            )
            self.send_message(chat_id, help_text)
            return

        if text.startswith("/status"):
            self.send_chat_action(chat_id, "typing")
            bat = get_battery_status()
            wifi = get_wifi_info()
            status_msg = (
                f"📊 Device Status — {self.config.device_name}\n\n"
                f"🔋 Battery: {bat.get('percentage', 'N/A')}% ({bat.get('status', 'Unknown')})\n"
                f"🌡️ Battery Temp: {bat.get('temperature', 'N/A')}°C\n"
                f"📶 WiFi SSID: {wifi.get('ssid', 'Disconnected')}\n"
                f"🌐 IP: {wifi.get('ip', 'N/A')}\n"
                f"🤖 Active Model: {self.config.model}"
            )
            self.send_message(chat_id, status_msg)
            return

        if text.startswith("/battery"):
            bat = get_battery_status()
            self.send_message(chat_id, f"🔋 Battery:\n{json.dumps(bat, indent=2)}")
            return

        if text.startswith("/torch"):
            parts = text.split()
            state = parts[1] if len(parts) > 1 else "on"
            res = set_torch(state)
            self.send_message(chat_id, f"🔦 Torch: {res.get('message', 'Updated')}")
            return

        if text.startswith("/photo"):
            self.send_chat_action(chat_id, "upload_photo")
            parts = text.split()
            cam_id = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            photo_res = take_photo(camera_id=cam_id)
            if photo_res.get("status") == "success" and "photo_path" in photo_res:
                self.send_photo(chat_id, photo_res["photo_path"], caption=f"📸 Photo from {'Front' if cam_id==1 else 'Back'} Camera")
            else:
                self.send_message(chat_id, f"⚠️ Photo failed: {photo_res.get('message')}")
            return

        if text.startswith("/sms"):
            self.send_chat_action(chat_id, "typing")
            sms_res = list_sms(limit=5)
            self.send_message(chat_id, f"📩 Recent SMS:\n{json.dumps(sms_res, indent=2)}")
            return

        if text.startswith("/calls"):
            self.send_chat_action(chat_id, "typing")
            calls_res = get_call_logs(limit=5)
            self.send_message(chat_id, f"📞 Recent Calls:\n{json.dumps(calls_res, indent=2)}")
            return

        if text.startswith("/exec"):
            cmd = text[5:].strip()
            if not cmd:
                self.send_message(chat_id, "⚠️ Usage: /exec <command>")
                return
            self.send_chat_action(chat_id, "typing")
            sh_res = execute_shell(cmd)
            out = sh_res.get("stdout") or sh_res.get("stderr") or "Done (No output)"
            self.send_message(chat_id, f"💻 Output:\n{out}")
            return

        if text.startswith("/reset") or text.startswith("/clear"):
            self.agent.memory.clear_history(session_id=str(chat_id))
            self.send_message(chat_id, "🧹 Conversation memory cleared!")
            return

        # Natural Language Processing via Autonomous Agent
        self.send_chat_action(chat_id, "typing")
        print(f"🤖 Processing through Agent LLM ({self.config.model})...")
        agent_res = self.agent.chat(user_input=text, session_id=str(chat_id))

        reply_content = agent_res.get("content", "Task processed.")
        print(f"📤 Sending reply to Telegram ({len(reply_content)} chars)...")
        self.send_message(chat_id, reply_content, parse_mode=None)

        # If any photos were captured during tool execution, send them!
        for photo_path in agent_res.get("photos", []):
            if os.path.exists(photo_path):
                self.send_chat_action(chat_id, "upload_photo")
                self.send_photo(chat_id, photo_path, caption="📸 Captured by Anamika")

    def run(self) -> None:
        """Starts the long-polling event loop."""
        if not self.token:
            print("❌ Error: Telegram token is not configured in ~/.anamika/config.json")
            sys.exit(1)

        print("\n" + "=" * 60)
        print("  🤖 ARTIFICIAL ANAMIKA TELEGRAM DAEMON STARTED")
        print(f"  • Device:  {self.config.device_name}")
        print(f"  • Model:   {self.config.model}")
        print(f"  • Users:   {self.allowed_users or 'ALL (Open)'}")
        print("=" * 60 + "\n")

        # Clear any stale webhook first
        self.clear_webhook()

        self.running = True
        while self.running:
            try:
                updates_res = self._request("getUpdates", {
                    "offset": self.last_update_id + 1,
                    "timeout": 20
                }, timeout=25)

                if updates_res.get("ok"):
                    for update in updates_res.get("result", []):
                        self.last_update_id = update.get("update_id", self.last_update_id)
                        if "message" in update:
                            self.handle_message(update["message"])
                else:
                    err_desc = updates_res.get("description", "Unknown Telegram Error")
                    print(f"⚠️ Telegram getUpdates error: {err_desc}")
                    time.sleep(3)

            except KeyboardInterrupt:
                print("\n🛑 Telegram Daemon stopped by user.")
                break
            except Exception as e:
                print(f"⚠️ Telegram Polling Exception: {e}")
                time.sleep(3)
