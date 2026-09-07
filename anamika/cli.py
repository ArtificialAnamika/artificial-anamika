"""Interactive CLI Interface & Command Dispatcher for Artificial Anamika."""

import os
import sys
import json
import argparse
from anamika.__version__ import __version__, __description__
from anamika.config import Config, run_setup_wizard, fetch_available_models, DEFAULT_CONFIG_PATH
from anamika.agent import Agent
from anamika.tools import default_registry
from anamika.telegram_bot import TelegramBot


def print_banner():
    print(r"""
    _         _   _  __ _      _       _        _                        _ _         
   / \   _ __| |_(_)/ _(_) ___(_) __ _| |      / \   _ __   __ _ _ __ ___ (_) | ____ _ 
  / _ \ | '__| __| | |_| |/ __| |/ _` | |     / _ \ | '_ \ / _` | '_ ` _ \| | |/ / _` |
 / ___ \| |  | |_| |  _| | (__| | (_| | |    / ___ \| | | | (_| | | | | | | |   < (_| |
/_/   \_\_|   \__|_|_| |_|\___|_|\__,_|_|   /_/   \_\_| |_|\__,_|_| |_| |_|_|_|\_\__,_|
    """)
    print(f"  ✨ Autonomous Android OS AI Employee — Version {__version__}")
    print("  " + "-" * 65)


def run_interactive_repl(config: Config):
    """Interactive terminal chat loop."""
    print_banner()
    print(f"  📱 Device:   {config.device_name}")
    print(f"  🧠 Model:    {config.model}")
    print(f"  ⚡ Endpoint: {config.endpoint}")
    print("  💡 Type 'exit', '/config', '/tools', or '/clear' to control session.\n")

    agent = Agent(config)
    session_id = "cli_session"

    while True:
        try:
            user_prompt = input("\033[1;36mAnant ❯\033[0m ").strip()
            if not user_prompt:
                continue

            if user_prompt.lower() in ("exit", "quit", "q"):
                print("\n👋 Goodbye Anant! Anamika session closed.\n")
                break

            if user_prompt.lower() == "/config":
                run_setup_wizard()
                config = Config()
                agent = Agent(config)
                continue

            if user_prompt.lower() == "/clear":
                agent.memory.clear_history(session_id)
                print("🧹 Conversation history cleared.\n")
                continue

            if user_prompt.lower() == "/tools":
                print("\n🛠️ REGISTERED ANDROID & SYSTEM TOOLS:")
                for name, tool in default_registry.tools.items():
                    print(f"  • \033[1;32m{name}\033[0m: {tool.description}")
                print()
                continue

            # Process prompt
            print("\033[1;33m⏳ Processing...\033[0m", end="\r")
            result = agent.chat(user_input=user_prompt, session_id=session_id)

            # Print tool executions if any
            if result.get("tools_executed"):
                for t in result["tools_executed"]:
                    print(f"\033[1;34m⚙️ [Tool: {t['name']}]\033[0m -> {json.dumps(t['result'], ensure_ascii=False)[:200]}")

            print(f"\033[1;35mAnamika ❯\033[0m {result['content']}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Session ended.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def list_models_cmd(config: Config):
    """Fetches and displays available models from current endpoint."""
    print(f"\n🔍 Fetching models from {config.endpoint}...")
    models = fetch_available_models(config.endpoint, config.api_key)
    if models:
        print(f"\n✅ Available Models ({len(models)}):")
        for m in models:
            print(f"  • {m}")
    else:
        print("⚠️ Could not fetch models or endpoint restricted /v1/models.\n")


def list_tools_cmd():
    """Lists all registered tools."""
    print("\n" + "=" * 60)
    print("🛠️  ARTIFICIAL ANAMIKA — ANDROID & SYSTEM TOOLS")
    print("=" * 60)
    for name, tool in default_registry.tools.items():
        print(f"\n📌 Tool: {name}")
        print(f"   Description: {tool.description}")
    print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Artificial Anamika — Autonomous Android OS AI Employee",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("command", nargs="?", default="chat", choices=["chat", "config", "telegram", "models", "tools", "version"], help="Command to run (default: chat)")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG_PATH, help="Path to config.json")
    parser.add_argument("-t", "--telegram", action="store_true", help="Launch Telegram Bot daemon")

    args = parser.parse_args()

    if args.command == "version":
        print(f"Artificial Anamika v{__version__}")
        return

    if args.command == "config":
        run_setup_wizard(args.config)
        return

    if args.command == "tools":
        list_tools_cmd()
        return

    cfg = Config(args.config)

    # First time run: launch wizard if not configured
    if not cfg.is_configured and args.command != "tools":
        print("⚠️ No valid configuration detected. Launching setup wizard...")
        cfg = run_setup_wizard(args.config)

    if args.command == "models":
        list_models_cmd(cfg)
        return

    if args.command == "telegram" or args.telegram:
        bot = TelegramBot(cfg)
        bot.run()
        return

    # Default: Interactive REPL
    run_interactive_repl(cfg)


if __name__ == "__main__":
    main()
