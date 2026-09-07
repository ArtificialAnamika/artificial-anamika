# ✨ Artificial Anamika (Anamika AI)

> **Ultra-Lightweight Autonomous AI Employee & Android Native Operating Agent for Termux & Beyond**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Android / Termux](https://img.shields.io/badge/Platform-Android%20%7C%20Termux%20%7C%20Linux-green.svg)](https://termux.dev)
[![Zero Bloat](https://img.shields.io/badge/Dependencies-Zero%20Bloat%20(Pure%20Python)-orange.svg)](https://python.org)
[![Custom Endpoints](https://img.shields.io/badge/LLM-Mandal%20%7C%20Claude%20%7C%20OpenAI%20%7C%20Groq%20%7C%20DeepSeek-purple.svg)](https://api.mandalworkforce.com)

```text
   _              __  __ _ _         
  /_\  _ _  __ _ |  \/  (_) |____ _  
 / _ \| ' \/ _` || |\/| | | / / _` | 
/_/ \_\_||_\__,_||_|  |_|_|_\_\__,_| 
```

**Artificial Anamika** is an ultra-lightweight, autonomous AI employee and system architect designed to run **natively inside Android Termux without heavy PRoot containers**. It bridges state-of-the-art Large Language Models (Claude 3.7 Sonnet, OpenAI, DeepSeek, custom API endpoints) directly to your Android device's hardware, telephony, camera, sensors, and operating system via real-time tool calling.

---

## ⚡ 1-Line Quick Install (Termux / Linux)

Run this single command inside your Termux terminal:

```bash
curl -sSL https://raw.githubusercontent.com/ArtificialAnamika/artificial-anamika/main/install.sh | bash
```

---

## 📲 Important Android Prerequisite: Termux:API App

For Android hardware access (Torch, SMS, Camera, Battery), Android requires the **Termux:API Companion APK** to be installed.

You can install it directly inside Termux with this 1-line command:

```bash
curl -sSL -o termux-api.apk "https://f-droid.org/repo/com.termux.api_51.apk" && termux-open termux-api.apk
```

Then run the built-in diagnostic doctor to verify and open permissions:
```bash
anamika doctor
```

---

## 🚀 Key Highlights & Philosophy

* 🎯 **Native Android Hardware Execution:** Controls Battery, Flashlight / Torch, Screen Brightness, Volume levels, Vibration, Sensors (light, accelerometer), WiFi, GPS location, and Camera directly.
* 📩 **Telephony & Communication:** Reads incoming SMS, auto-extracts OTP verification codes, sends SMS, inspects call logs, and searches contacts.
* 🗣️ **UI, Speech & Alerts:** Native Android Text-to-Speech (TTS) voice, popup toast alerts, high-priority notifications, clipboard read/write, and dialog prompts.
* 📱 **Android OS & Intent Automation:** Launches any app (`am start` / `monkey`), opens web URLs, opens system settings, plays audio, and downloads files.
* 🤖 **24x7 Telegram Bot Daemon:** Connects to your dedicated Telegram bot (e.g. `@OnePlusTabHermes_bot`) with whitelist security, command routing, and direct camera photo uploads.
* ⚙️ **Custom LLM Provider Wizard:** Interactive setup for Base URL / Endpoint, API Key, and **dynamic `/v1/models` discovery with pagination & keyword search (`/query`)**.
* 🩺 **Built-in Permission Doctor:** One command (`anamika doctor`) to test all hardware permissions and trigger Android app settings.
* 🪶 **Zero-Bloat / Pure Python:** Runs on standard Python 3 with zero heavy C/Rust dependencies (`tiktoken`, `playwright`, etc. are NOT required).

---

## 🛠️ Interactive Configuration Wizard

On first launch (or by running `anamika config`), Anamika guides you through a streamlined setup:

```text
============================================================
  ✨ ARTIFICIAL ANAMIKA (ANAMIKA AI) — SETUP WIZARD
  Ultra-Lightweight Autonomous Android OS AI Employee
============================================================

📌 STEP 1: SELECT OR ENTER LLM ENDPOINT URL
  [1] Mandal Workforce Custom Endpoint (https://api.mandalworkforce.com/v1)
  [2] OpenAI Official API (https://api.openai.com/v1)
  [3] OpenRouter API (https://openrouter.ai/api/v1)
  [4] Groq Fast Inference (https://api.groq.com/openai/v1)
  [5] DeepSeek Official API (https://api.deepseek.com/v1)
  [6] Custom Endpoint (Self-hosted / vLLM / Ollama / LiteLLM)

📌 STEP 2: ENTER API KEY
📌 STEP 3: DYNAMIC MODEL SELECTION (Auto-probes /v1/models with pagination & search)
📌 STEP 4: TELEGRAM BOT TOKEN & USER WHITELIST
📌 STEP 5: DEVICE IDENTIFIER (e.g. OnePlus-Tab)
```

---

## 💻 CLI Commands & Daemon Control

| Command | Action |
|---|---|
| `anamika` | Start interactive terminal chat REPL |
| `anamika telegram start` | Start 24x7 Telegram Bot Daemon in background (with wake lock) |
| `anamika telegram stop` | Stop running background Telegram daemon |
| `anamika telegram restart` | Restart background Telegram daemon |
| `anamika telegram status` | Check if daemon is running, PID, and view recent logs |
| `anamika telegram logs` | View daemon logs (`-f` to stream live) |
| `anamika telegram run` | Run Telegram bot in foreground (debug mode) |
| `anamika config` | Launch interactive configuration wizard |
| `anamika doctor` | Run permission diagnostics & Android APK helper |
| `anamika models` | Fetch & list available models from endpoint |
| `anamika tools` | Display full catalog of registered Android tools |
| `anamika version` | Display installed version |

---

## 🤖 Telegram Bot Control

When running in daemon mode (`anamika telegram`), Anamika listens on Telegram and accepts natural language instructions:

* *"Battery check karo aur flashlight on kar do"*
* *"Back camera se photo khinch kar yaha bhejo"*
* *"Recent OTP SMS dikhao"*
* *"Screen par 'Task Done' ka toast alert show karo"*
* *"WhatsApp open karo"*
* *"Termux me `df -h` command run karo"*

### Quick Slash Commands:
* `/status` — Real-time device health, battery %, WiFi SSID, active model
* `/battery` — Detailed battery JSON metrics
* `/torch <on|off>` — Fast flashlight switch
* `/photo <0|1>` — Capture and receive photo instantly (0=back, 1=front)
* `/sms` — View recent SMS messages and OTPs
* `/exec <cmd>` — Execute bash command in Termux
* `/reset` — Clear conversation history

---

## 📂 Project Architecture

```text
artificial-anamika/
├── anamika/
│   ├── __init__.py
│   ├── __version__.py
│   ├── config.py              # Configuration manager & model discovery wizard
│   ├── client.py              # Zero-dependency OpenAI/Claude REST client
│   ├── agent.py               # Multi-turn reasoning & tool execution engine
│   ├── memory.py              # SQLite persistent conversation memory
│   ├── prompt.py              # SOUL & Hinglish technical employee persona
│   ├── telegram_bot.py        # 24x7 Telegram long-polling daemon
│   ├── cli.py                 # Terminal REPL & command dispatcher
│   ├── doctor.py              # Diagnostic permission doctor & APK installer
│   └── tools/                 # Native Android & System Tools
│       ├── hardware.py        # Battery, Torch, Brightness, Volume, Sensors
│       ├── telephony.py       # SMS reader/sender, OTPs, Call logs, Contacts
│       ├── ui_alerts.py       # TTS Speech, Toasts, Notifications, Clipboard
│       ├── android_os.py      # App launching, Intents, Settings, Downloads
│       ├── shell_system.py    # Bash runner, File I/O, Storage, Processes
│       └── camera.py          # Photo capture & Telegram media dispatcher
├── docs/
│   ├── ARCHITECTURE.md        # Deep dive into system architecture
│   ├── ANDROID_TOOLS.md       # Complete tools and schema reference
│   ├── SOUL.md                # Persona, Mission & Operating standard
│   └── SOP_DEPLOYMENT.md      # Step-by-step deployment guide
├── scripts/
│   ├── run_daemon.sh          # Background startup script with wake lock
│   └── termux_healthcheck.sh  # Diagnostic healthcheck script
├── tests/                     # Unit & integration test suite
├── install.sh                 # 1-Line Termux automated installer
├── main.py                    # Standalone executable entrypoint
└── pyproject.toml             # Python packaging
```

---

## 🔒 Security & Privacy

1. **Telegram Whitelist:** Only user IDs specified in `allowed_telegram_users` can interact with the bot. Unauthorized requests are strictly rejected.
2. **Local Memory:** Conversation history and durable facts remain stored locally in SQLite (`~/.anamika/memory.db`).
3. **Protected Configuration:** Configuration files are restricted (`chmod 600`) to protect API keys.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
