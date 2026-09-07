"""Tool Registry and Export System for Artificial Anamika."""

from anamika.tools.base import ToolRegistry, Tool, run_command
from anamika.tools.hardware import (
    get_battery_status,
    set_torch,
    vibrate,
    set_brightness,
    set_volume,
    get_wifi_info,
    get_location,
    get_sensor_data
)
from anamika.tools.telephony import (
    list_sms,
    send_sms,
    get_call_logs,
    list_contacts,
    get_cell_info
)
from anamika.tools.ui_alerts import (
    tts_speak,
    show_toast,
    show_notification,
    get_clipboard,
    set_clipboard,
    show_dialog
)
from anamika.tools.android_os import (
    launch_app,
    open_url,
    open_settings,
    play_media,
    download_file
)
from anamika.tools.shell_system import (
    execute_shell,
    read_file,
    write_file,
    get_storage_info,
    list_processes
)
from anamika.tools.camera import take_photo


def create_default_registry() -> ToolRegistry:
    """Creates and populates the default tool registry with all Android & System tools."""
    registry = ToolRegistry()

    # Hardware & Sensors
    registry.register(get_battery_status)
    registry.register(set_torch)
    registry.register(vibrate)
    registry.register(set_brightness)
    registry.register(set_volume)
    registry.register(get_wifi_info)
    registry.register(get_location)
    registry.register(get_sensor_data)

    # Telephony & SMS
    registry.register(list_sms)
    registry.register(send_sms)
    registry.register(get_call_logs)
    registry.register(list_contacts)
    registry.register(get_cell_info)

    # UI & Alerts
    registry.register(tts_speak)
    registry.register(show_toast)
    registry.register(show_notification)
    registry.register(get_clipboard)
    registry.register(set_clipboard)
    registry.register(show_dialog)

    # Android OS & Intents
    registry.register(launch_app)
    registry.register(open_url)
    registry.register(open_settings)
    registry.register(play_media)
    registry.register(download_file)

    # Linux Shell & System
    registry.register(execute_shell)
    registry.register(read_file)
    registry.register(write_file)
    registry.register(get_storage_info)
    registry.register(list_processes)

    # Camera
    registry.register(take_photo)

    return registry


default_registry = create_default_registry()

__all__ = [
    "ToolRegistry",
    "Tool",
    "run_command",
    "create_default_registry",
    "default_registry"
]
