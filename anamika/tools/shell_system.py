"""Linux Shell, Filesystem, Storage & Process Tools for Termux."""

import os
import shutil
from typing import Dict, Any
from anamika.tools.base import run_command


def execute_shell(command: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute a Linux shell command in the Termux environment (e.g. 'ls', 'curl', 'ps', 'git', 'df', 'top')."""
    res = run_command(command, timeout=timeout, shell=True)
    return {
        "success": res["success"],
        "exit_code": res["exit_code"],
        "stdout": res["stdout"][:4000] if len(res["stdout"]) > 4000 else res["stdout"],
        "stderr": res["stderr"][:1000] if len(res["stderr"]) > 1000 else res["stderr"],
        "truncated": len(res["stdout"]) > 4000
    }


def read_file(path: str, max_lines: int = 200) -> Dict[str, Any]:
    """Read contents of a text file from the filesystem."""
    expanded_path = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(expanded_path):
        return {"error": f"File not found: {path}"}
        
    try:
        with open(expanded_path, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(max_lines)]
            content = "".join(lines)
            return {
                "status": "success",
                "path": expanded_path,
                "lines_read": len(lines),
                "content": content
            }
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}


def write_file(path: str, content: str) -> Dict[str, Any]:
    """Write or overwrite text content to a file."""
    expanded_path = os.path.abspath(os.path.expanduser(path))
    try:
        os.makedirs(os.path.dirname(expanded_path), exist_ok=True)
        with open(expanded_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {
            "status": "success",
            "path": expanded_path,
            "bytes_written": len(content.encode("utf-8"))
        }
    except Exception as e:
        return {"error": f"Failed to write file: {e}"}


def get_storage_info() -> Dict[str, Any]:
    """Check storage space (total, used, free) on internal storage and /sdcard."""
    res = run_command(["df", "-h"], timeout=10)
    return {
        "status": "success" if res["success"] else "error",
        "output": res["stdout"] or res["stderr"]
    }


def list_processes(filter_name: str = "") -> Dict[str, Any]:
    """List running processes in Termux with optional name filter."""
    res = run_command(["ps", "-ef"] if shutil.which("ps") else ["ps"], timeout=10)
    if res["success"]:
        lines = res["stdout"].splitlines()
        if filter_name:
            f_low = filter_name.lower()
            lines = [l for l in lines if f_low in l.lower()]
        return {
            "status": "success",
            "count": len(lines),
            "processes": "\n".join(lines[:40])
        }
    return {"status": "error", "message": res["stderr"]}
