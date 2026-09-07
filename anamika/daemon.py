"""Daemon Manager for Background 24x7 Telegram Bot."""

import os
import sys
import time
import signal
import subprocess
from typing import Optional

PID_FILE = os.path.expanduser("~/.anamika/daemon.pid")
LOG_FILE = os.path.expanduser("~/.anamika/daemon.log")


def get_running_pid() -> Optional[int]:
    """Returns PID if daemon is currently running, else None."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            # Check if process is alive
            os.kill(pid, 0)
            return pid
        except (ValueError, OSError, ProcessLookupError):
            try:
                os.remove(PID_FILE)
            except Exception:
                pass
    return None


def acquire_wake_lock():
    """Acquires Termux wake lock to prevent Android from sleeping."""
    try:
        subprocess.run(["termux-wake-lock"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
    except Exception:
        pass


def release_wake_lock():
    """Releases Termux wake lock."""
    try:
        subprocess.run(["termux-wake-unlock"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
    except Exception:
        pass


def start_daemon(config_path: str = None) -> bool:
    """Starts the Telegram daemon in background with wake lock and log redirection."""
    existing_pid = get_running_pid()
    if existing_pid:
        print(f"ℹ️ Telegram Daemon is already running (PID: {existing_pid}).")
        print(f"  • Status: anamika telegram status")
        print(f"  • Stop:   anamika telegram stop")
        return True

    acquire_wake_lock()
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    log_fp = open(LOG_FILE, "a", encoding="utf-8")
    
    cmd = [sys.executable, "-m", "anamika.cli", "telegram", "--foreground"]
    if config_path:
        cmd.extend(["-c", config_path])

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=log_fp,
            stderr=log_fp,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        pid = proc.pid
        with open(PID_FILE, "w") as f:
            f.write(str(pid))

        # Give it a moment to initialize
        time.sleep(1)

        print("\n" + "=" * 60)
        print("  🚀 ARTIFICIAL ANAMIKA TELEGRAM DAEMON STARTED!")
        print("=" * 60)
        print(f"  • Status: 🟢 RUNNING in background (24x7)")
        print(f"  • PID:    {pid}")
        print(f"  • Logs:   {LOG_FILE}")
        print(f"  • View:   anamika telegram logs")
        print(f"  • Stop:   anamika telegram stop")
        print("=" * 60 + "\n")
        return True
    except Exception as e:
        print(f"❌ Failed to start daemon: {e}")
        return False


def stop_daemon() -> bool:
    """Stops the running Telegram daemon gracefully."""
    pid = get_running_pid()
    if not pid:
        print("ℹ️ Telegram Daemon is not currently running.")
        return True

    print(f"🛑 Stopping Telegram Daemon (PID: {pid})...")
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        # Verify killed
        try:
            os.kill(pid, 0)
            # Force kill if still alive
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass

        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)

        release_wake_lock()
        print("✅ Telegram Daemon stopped successfully.")
        return True
    except Exception as e:
        print(f"⚠️ Error stopping daemon: {e}")
        return False


def restart_daemon(config_path: str = None) -> bool:
    """Restarts the Telegram daemon."""
    stop_daemon()
    time.sleep(1)
    return start_daemon(config_path)


def status_daemon():
    """Prints current daemon status and last log entries."""
    pid = get_running_pid()
    print("\n" + "=" * 60)
    print("  🤖 ARTIFICIAL ANAMIKA DAEMON STATUS")
    print("=" * 60)

    if pid:
        print(f"  • State: 🟢 RUNNING (Background 24x7)")
        print(f"  • PID:   {pid}")
        print(f"  • Logs:  {LOG_FILE}")
    else:
        print("  • State: 🔴 STOPPED")
        print("  • Start: anamika telegram start")

    if os.path.exists(LOG_FILE):
        print("\n📜 RECENT LOGS (Last 6 lines):")
        print("-" * 60)
        try:
            with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                for line in lines[-6:]:
                    print(f"  {line.rstrip()}")
        except Exception:
            pass

    print("=" * 60 + "\n")


def show_logs(follow: bool = False):
    """Displays daemon log output."""
    if not os.path.exists(LOG_FILE):
        print("ℹ️ No log file found yet. (Start daemon first: anamika telegram start)")
        return

    if follow:
        print(f"📡 Streaming logs from {LOG_FILE} (Ctrl+C to exit)...\n")
        try:
            subprocess.run(["tail", "-f", LOG_FILE])
        except KeyboardInterrupt:
            print("\n👋 Stopped watching logs.")
    else:
        print(f"\n📜 DAEMON LOGS ({LOG_FILE}):")
        print("-" * 60)
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            for line in lines[-35:]:
                print(line.rstrip())
        print("-" * 60 + "\n")
