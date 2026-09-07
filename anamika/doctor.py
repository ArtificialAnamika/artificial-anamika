"""System Diagnostics & Android Permission Doctor for Artificial Anamika."""

import os
import sys
import time
import shutil
import subprocess
import urllib.request
from anamika.tools.base import run_command

APK_URL_FDROID = "https://f-droid.org/repo/com.termux.api_51.apk"
APK_URL_GITHUB = "https://github.com/termux/termux-api/releases/download/v0.51.0/termux-api_v0.51.0+github-debug.apk"


def is_app_installed(package_name: str) -> bool:
    """Checks if an Android app package is installed on the system."""
    res = run_command(["pm", "path", package_name], timeout=5)
    return res["success"] and "package:" in res["stdout"]


def open_settings_page(package_name: str) -> bool:
    """Opens Android App Info settings page for a package."""
    cmd = ["am", "start", "-a", "android.settings.APPLICATION_DETAILS_SETTINGS", "-d", f"package:{package_name}"]
    res = run_command(cmd, timeout=5)
    return res["success"]


def download_and_install_termux_api_apk():
    """Downloads Termux:API APK directly and triggers Android Package Installer."""
    cache_dir = os.path.expanduser("~/.anamika/downloads")
    os.makedirs(cache_dir, exist_ok=True)
    apk_path = os.path.join(cache_dir, "termux-api.apk")

    print(f"\n📥 Downloading Termux:API APK...")
    try:
        # Try F-Droid first, fallback to GitHub
        try:
            urllib.request.urlretrieve(APK_URL_FDROID, apk_path)
        except Exception:
            urllib.request.urlretrieve(APK_URL_GITHUB, apk_path)

        if os.path.exists(apk_path) and os.path.getsize(apk_path) > 100000:
            print(f"✅ Downloaded ({os.path.getsize(apk_path) // 1024} KB).")
            print("🚀 Launching Android Package Installer...")
            
            # Use termux-open if available
            if shutil.which("termux-open"):
                run_command(["termux-open", "--view", apk_path])
            else:
                run_command(["am", "start", "-a", "android.intent.action.VIEW", "-d", f"file://{apk_path}", "-t", "application/vnd.android.package-archive"])
            
            print("\n👉 Android screen par popup aayega — 'Install' / 'Update' par tap karein.")
        else:
            print("❌ Downloaded file seems incomplete.")
    except Exception as e:
        print(f"❌ Failed to download APK: {e}")
        print(f"👉 Please download manually from: {APK_URL_FDROID}")


def run_permission_doctor():
    """Runs interactive diagnostic tests for all Android permissions and guides the user."""
    print("\n" + "=" * 65)
    print("  🩺 ARTIFICIAL ANAMIKA — ANDROID PERMISSION DOCTOR")
    print("=" * 65 + "\n")

    issues_found = False

    # 1. Check if termux-api CLI is installed
    print("1. Checking Termux:API CLI Package...")
    if shutil.which("termux-battery-status"):
        print("   ✅ termux-api CLI package is installed in Termux.")
    else:
        print("   ❌ termux-api CLI is MISSING!")
        print("      Run: pkg install -y termux-api")
        issues_found = True

    # 2. Check if Termux:API Companion APK is installed
    print("\n2. Checking Termux:API Android App (APK)...")
    app_installed = is_app_installed("com.termux.api")
    if app_installed:
        print("   ✅ Termux:API Android App is INSTALLED on the phone.")
    else:
        print("   ❌ Termux:API Android App is NOT INSTALLED!")
        print("      👉 Yeh Android Companion App hai jo Termux ko phone ke hardware se connect karti hai.")
        issues_found = True

        choice = input("\n📥 Kya aap Termux:API APK abhi direct download & install karna chahte hain? (y/n): ").strip().lower()
        if choice in ("y", "yes", ""):
            download_and_install_termux_api_apk()
            return

    # 3. Check Battery API
    print("\n3. Testing Battery API...")
    res_bat = run_command(["termux-battery-status"], timeout=6)
    if res_bat["success"] and res_bat["stdout"]:
        print("   ✅ Battery API: Working")
    else:
        print("   ⚠️ Battery API: Failed or timed out")
        issues_found = True

    # 4. Check Torch / Camera Permission
    print("\n4. Testing Torch / Camera Permission...")
    res_torch = run_command(["termux-torch", "on"], timeout=6)
    if res_torch["success"]:
        time.sleep(0.5)
        run_command(["termux-torch", "off"], timeout=5)
        print("   ✅ Torch / Flashlight: Working (Camera permission is granted)")
    else:
        print("   ❌ Torch / Camera: FAILED (Permission Denied)")
        print("      👉 Android me Torch use karne ke liye 'Camera' permission chahiye hoti hai.")
        issues_found = True

    # 5. Check SMS Permission
    print("\n5. Testing SMS Permission...")
    res_sms = run_command(["termux-sms-list", "-l", "1"], timeout=6)
    if res_sms["success"] and res_sms["stdout"]:
        print("   ✅ SMS API: Working (SMS permission is granted)")
    else:
        print("   ❌ SMS API: FAILED (Permission Denied)")
        print("      👉 SMS read/send karne ke liye 'SMS' permission chahiye hoti hai.")
        issues_found = True

    # 6. Check Storage Permission
    print("\n6. Testing Storage Access (/sdcard)...")
    if os.path.exists("/sdcard") and os.access("/sdcard", os.R_OK):
        print("   ✅ Storage: Working (/sdcard is readable)")
    else:
        print("   ⚠️ Storage Permission missing.")
        print("      Run: termux-setup-storage")
        issues_found = True

    print("\n" + "=" * 65)
    if issues_found and app_installed:
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
    elif not issues_found:
        print("🎉 ALL ANDROID PERMISSIONS ARE PROPERLY CONFIGURED & WORKING!")
    print("=" * 65 + "\n")
