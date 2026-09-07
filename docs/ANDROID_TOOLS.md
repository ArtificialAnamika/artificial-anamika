# Artificial Anamika — Android Tools & Capabilities Catalog

Anamika provides natural language control over all core Android hardware and OS subsystems.

---

## 1. Hardware & Sensors (`anamika/tools/hardware.py`)

| Tool Name | Underlying Android/Termux Command | Description |
|---|---|---|
| `get_battery_status` | `termux-battery-status` | Returns percentage, health, temperature, status |
| `set_torch` | `termux-torch <on/off>` | Turns camera flashlight ON or OFF |
| `vibrate` | `termux-vibrate -d <ms>` | Vibrates the phone for specified milliseconds |
| `set_brightness` | `termux-brightness <0-255>` | Sets screen brightness level |
| `set_volume` | `termux-volume <stream> <val>` | Sets volume for music, ring, call, alarm, notification |
| `get_wifi_info` | `termux-wifi-connectioninfo` | Returns WiFi SSID, BSSID, IP, RSSI, speed |
| `get_location` | `termux-location -p network` | Retrieves GPS/network latitude & longitude |
| `get_sensor_data` | `termux-sensor -n 1` | Reads light, accelerometer, step counter data |

---

## 2. Telephony & SMS (`anamika/tools/telephony.py`)

| Tool Name | Underlying Android/Termux Command | Description |
|---|---|---|
| `list_sms` | `termux-sms-list` | Reads recent SMS, auto-extracts OTP verification codes |
| `send_sms` | `termux-sms-send -n <num> <msg>` | Sends SMS to any phone number |
| `get_call_logs` | `termux-telephony-call-log` | Returns incoming, outgoing, and missed call history |
| `list_contacts` | `termux-contact-list` | Searches phonebook contacts |
| `get_cell_info` | `termux-telephony-cellinfo` | Inspects SIM carrier & cellular signal status |

---

## 3. UI, Speech & Notifications (`anamika/tools/ui_alerts.py`)

| Tool Name | Underlying Android/Termux Command | Description |
|---|---|---|
| `tts_speak` | `termux-tts-speak` | Speaks text aloud through device speakers |
| `show_toast` | `termux-toast` | Displays popup Toast message on screen |
| `show_notification` | `termux-notification` | Posts high-priority Android system notification |
| `get_clipboard` | `termux-clipboard-get` | Reads copied text from Android clipboard |
| `set_clipboard` | `termux-clipboard-set` | Writes text to Android clipboard |
| `show_dialog` | `termux-dialog` | Displays interactive prompt input on screen |

---

## 4. Android OS & Apps (`anamika/tools/android_os.py`)

| Tool Name | Underlying Android/Termux Command | Description |
|---|---|---|
| `launch_app` | `monkey` / `am start` | Opens WhatsApp, YouTube, Chrome, Telegram, Settings |
| `open_url` | `termux-open-url` | Opens any URL in default web browser |
| `open_settings` | `am start -a android.settings.*` | Opens WiFi, Bluetooth, Battery, Display settings |
| `play_media` | `termux-media-player` | Plays, pauses, stops local audio tracks |
| `download_file` | `termux-download` | Enqueues background file download via Android manager |

---

## 5. Camera & Photography (`anamika/tools/camera.py`)

| Tool Name | Underlying Android/Termux Command | Description |
|---|---|---|
| `take_photo` | `termux-camera-photo -c <0/1>` | Captures photo (0=back, 1=front) and saves to disk |

---

## 6. Linux Shell & Filesystem (`anamika/tools/shell_system.py`)

| Tool Name | Description |
|---|---|
| `execute_shell` | Executes arbitrary bash/sh commands in Termux |
| `read_file` | Reads text file from disk |
| `write_file` | Writes/overwrites file on disk |
| `get_storage_info` | Displays free/used disk space (`df -h`) |
| `list_processes` | Lists active background processes |
