# Artificial Anamika — Architecture & System Design

## 1. High-Level Architecture

Artificial Anamika is built from scratch as an **Ultra-Lightweight, Zero-Bloat Android Operating AI Agent**. Unlike heavy agent frameworks (LangChain, AutoGen, or PRoot containers), Anamika runs purely on Python standard library with native Termux Unix domain socket integration.

```text
[Telegram Bot (@OnePlusTabHermes_bot) / Interactive CLI REPL]
                         │
                         ▼
        ┌──────────────────────────────────┐
        │   Anamika Core Agent Engine      │
        │  • Event Poller & Security Check │
        │  • SQLite Local Memory Store     │
        │  • Tool Schema Serializer        │
        └─────────────────┬────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
┌───────────────┐               ┌───────────────────┐
│ LLM Provider  │ ◄─(Tool Call)─┤ Tool Dispatcher   │
│ (Custom /     │               │ (Native Android & │
│ Mandal API)   │ ─(Exec Cmd)──►│ Termux Engine)    │
└───────────────┘               └─────────┬─────────┘
                                          │
    ┌─────────────────────────────────────┼─────────────────────────────────────┐
    ▼                                     ▼                                     ▼
[Termux:API IPC]                   [Android Intents (am)]              [Linux Shell Core]
(SMS, Battery, Torch,             (App Launch, URLs, Settings,        (Bash, Git, Network,
 Camera, TTS, Clipboard)           Media Player, Downloads)            Storage, Cron Jobs)
```

---

## 2. Key Components

### 2.1 Configuration Manager & Model Fetcher (`anamika/config.py`)
- Provides an interactive wizard to configure:
  1. Base URL / Endpoint (Presets: Mandal Workforce, OpenAI, OpenRouter, Groq, DeepSeek, Custom).
  2. API Key.
  3. **Automated Model Probing (`/v1/models`):** Fetches the full list of available models from the endpoint dynamically and presents an interactive picker.
  4. Telegram Bot Token & Security Whitelist (`allowed_telegram_users`).
  5. Device Name (e.g. `OnePlus-Tab`).

### 2.2 LLM REST Client (`anamika/client.py`)
- Built using Python's standard `urllib.request`, `ssl`, and `json`.
- Zero C-extension / Rust compilation requirements.
- Native OpenAI/Claude-compatible tool calling (`tools`, `tool_choice: "auto"`).

### 2.3 Tool Registry & Android Hardware Dispatcher (`anamika/tools/`)
- Dynamically converts Python functions into JSON tool schemas.
- Interfaces directly with `termux-*` and Android `am` intent binaries.

### 2.4 Persistent Memory (`anamika/memory.py`)
- SQLite-backed conversation history and durable device facts.
- Survives reboots and agent restarts.

### 2.5 Telegram Bot Daemon (`anamika/telegram_bot.py`)
- 24x7 long-polling background worker.
- Whitelist protection (blocks unauthorized users).
- Automatically sends captured camera photos directly to Telegram.
