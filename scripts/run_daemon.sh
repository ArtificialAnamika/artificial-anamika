#!/bin/bash
# Starts Artificial Anamika Telegram Daemon in background with wake lock

if command -v termux-wake-lock >/dev/null 2>&1; then
    echo "Acquiring Termux wake lock to prevent background sleep..."
    termux-wake-lock
fi

LOG_FILE="$HOME/.anamika/daemon.log"
mkdir -p "$HOME/.anamika"

echo "Starting Artificial Anamika Telegram Daemon..."
nohup python3 -m anamika.cli telegram > "$LOG_FILE" 2>&1 &
PID=$!
echo "Daemon started with PID: $PID"
echo "Logs streaming to: $LOG_FILE"
