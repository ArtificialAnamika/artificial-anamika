#!/bin/bash
# Tests Termux API commands and reports readiness

echo "=== ARTIFICIAL ANAMIKA ANDROID HEALTHCHECK ==="
date

echo -e "\n1. Checking Python..."
python3 --version || echo "Python missing"

echo -e "\n2. Checking Termux:API commands..."
for cmd in termux-battery-status termux-torch termux-vibrate termux-tts-speak termux-sms-list termux-camera-photo; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "  [OK] $cmd is available"
    else
        echo "  [FAIL] $cmd missing (Run: pkg install termux-api)"
    fi
done

echo -e "\n3. Testing Battery API..."
termux-battery-status || echo "termux-battery-status returned non-zero (Check Termux:API app permissions)"

echo -e "\n=== HEALTHCHECK FINISHED ==="
