# SOP — Deploying Artificial Anamika on Android / Termux

## Objective
Standard Operating Procedure for installing, configuring, and verifying Artificial Anamika on any Android device (OnePlus Tab, Smartphone, Node).

---

## 1. Prerequisites on Android Device
1. **Termux App:** Installed from F-Droid (or GitHub Releases).
2. **Termux:API App:** Installed from F-Droid with permissions enabled (Camera, Location, SMS, Contacts, Phone).

---

## 2. 1-Line Automated Installation
Run the following single command inside Termux:

```bash
curl -sSL https://raw.githubusercontent.com/ArtificialAnamika/artificial-anamika/main/install.sh | bash
```

---

## 3. Interactive Configuration Steps
When the Setup Wizard appears:
1. **Endpoint:** Choose preset (e.g. `[1] Mandal Workforce Custom Endpoint`) or enter custom URL.
2. **API Key:** Paste your API key.
3. **Model Selection:** The wizard probes `/v1/models` automatically. Pick your model number (e.g. `claude-3-7-sonnet-20250219`).
4. **Telegram Bot Token:** Enter Bot token for `@OnePlusTabHermes_bot` (or your dedicated bot).
5. **Allowed Telegram User IDs:** Enter your Telegram ID (e.g. `7361027380`).
6. **Device Name:** Enter device identifier (e.g. `OnePlus-Tab`).

---

## 4. Operational Commands

### Interactive Chat Mode
```bash
anamika
```

### Start 24x7 Telegram Bot Daemon
```bash
anamika telegram
```

### Run in Background (with wake lock)
```bash
bash ~/.anamika/app/scripts/run_daemon.sh
```

### Reconfigure Anytime
```bash
anamika config
```

### List All Available Tools
```bash
anamika tools
```
