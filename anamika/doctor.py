"""System Diagnostics & Android Permission Doctor for Artificial Anamika."""

import os
import sys
import time
import shutil
import subprocess
from anamika.tools.base import run_command


def open_settings_page(package_name: str) -> bool:
    """Opens Android App Info settings page for a package."""
    cmd = ["am", "start", "-a", "android.settings.APPLICATION_DETAILS_SETTINGS", "-d", f"package:{package_name}"]
    res = run_command(cmd, timeout=5)
    return res["success"]


def run_permission_doctor():
    """Runs interactive diagnostic tests for all Android permissions and guides the user."""
    print("\n" + "=" * 65)
    print("  🩺 ARTIFICIAL ANAMIKA — ANDROID PERMISSION DOCTOR")
    print("=" * 65 + "\n")

    issues_found = False

    # 1. Check if termux-api CLI is installed
    print("1. Checking Termux:API CLI Package...")
    if shutil.which("termux-battery-status"):
        print("   ✅ termux-api CLI is installed in Termux.")
    else:
        print("   ❌ termux-api CLI is MISSING!")
        print("      Run: pkg install -y termux-api")
        issues_found = True

    # 2. Check Battery API
    print("\n2. Testing Battery API...")
    res_bat = run_command(["termux-battery-status"], timeout=6)
    if res_bat["success"] and res_bat["stdout"]:
        print("   ✅ Battery API: Working")
    else:
        print("   ⚠️ Battery API: Failed or timed out")
        issues_found = True

    # 3. Check Torch / Camera Permission
    print("\n3. Testing Torch / Camera Permission...")
    res_torch = run_command(["termux-torch", "on"], timeout=6)
    if res_torch["success"]:
        time.sleep(0.5)
        run_command(["termux-torch", "off"], timeout=5)
        print("   ✅ Torch / Flashlight: Working (Camera permission is granted)")
    else:
        print("   ❌ Torch / Camera: FAILED (Permission Denied)")
        print("      👉 Android me Torch use karne ke liye 'Camera' permission chahiye hoti hai.")
        issues_found = True

    # 4. Check SMS Permission
    print("\n4. Testing SMS Permission...")
    res_sms = run_command(["termux-sms-list", "-l", "1"], timeout=6)
    if res_sms["success"] and res_sms["stdout"]:
        print("   ✅ SMS API: Working (SMS permission is granted)")
    else:
        print("   ❌ SMS API: FAILED (Permission Denied)")
        print("      👉 SMS read/send karne ke liye 'SMS' permission chahiye hoti hai.")
        issues_found = True

    # 5. Check Storage Permission
    print("\n5. Testing Storage Access (/sdcard)...")
    if os.path.exists("/sdcard") and os.access("/sdcard", os.R_OK):
        print("   ✅ Storage: Working (/sdcard is readable)")
    else:
        print("   ⚠️ Storage Permission missing.")
        print("      Run: termux-setup-storage")
        issues_found = True

    print("\n" + "=" * 65)
    if issues_found:
        print("🔧 FIXING PERMISSION ISSUES ON ANDROID / ONEPLUS TAB:")
        print("-----------------------------------------------------------------")
        print("Android OS me permissions 'Termux:API' APK ko deni hoti hain:")
        print("  1. Camera Permission ➔ Required for Flashlight/Torch & Photos")
        print("  2. SMS Permission    ➔ Required for Reading OTPs & Sending SMS")
        print("  3. Location          ➔ Required for WiFi & GPS")
        print("  4. Contacts / Phone  ➔ Required for Contacts & Call logs")
        print("  5. Battery           ➔ Set to 'Unrestricted' / 'Don't Optimize'")
        print("-----------------------------------------------------------------")

        choice = input("\n📱 Kya aap 'Termux:API' ka Android Settings page abhi open karna chahte hain? (y/n): ").strip().lower()
        if choice in ("y", "yes", ""):
            print("🚀 Opening Termux:API App Info screen...")
            open_settings_page("com.termux.api")
            print("\n👉 Settings me 'Permissions' par tap karke Camera, SMS, Location enable karein.")
    else:
        print("🎉 ALL ANDROID PERMISSIONS ARE PROPERLY CONFIGURED & WORKING!")
    print("=" * 65 + "\n")
