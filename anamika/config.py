"""Configuration Manager & Interactive Setup Wizard for Artificial Anamika."""

import os
import sys
import json
import ssl
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

DEFAULT_CONFIG_DIR = os.path.expanduser("~/.anamika")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_DIR, "config.json")

DEFAULT_PRESETS = [
    {
        "name": "Mandal Workforce Custom Endpoint",
        "url": "https://api.mandalworkforce.com/v1",
        "default_model": "claude-3-7-sonnet-20250219"
    },
    {
        "name": "OpenAI Official API",
        "url": "https://api.openai.com/v1",
        "default_model": "gpt-4o"
    },
    {
        "name": "OpenRouter API",
        "url": "https://openrouter.ai/api/v1",
        "default_model": "anthropic/claude-3.7-sonnet"
    },
    {
        "name": "Groq Fast Inference",
        "url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile"
    },
    {
        "name": "DeepSeek Official API",
        "url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat"
    },
    {
        "name": "Custom Endpoint (Self-hosted / vLLM / Ollama / LiteLLM)",
        "url": "",
        "default_model": ""
    }
]


class Config:
    """Manages Anamika configuration persistence and retrieval."""

    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        self.config_path = os.path.abspath(os.path.expanduser(config_path))
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Warning: Failed to load config from {self.config_path}: {e}")
        return {}

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        try:
            os.chmod(self.config_path, 0o600)
        except Exception:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()

    @property
    def endpoint(self) -> str:
        url = self.get("endpoint", "https://api.mandalworkforce.com/v1")
        return url.rstrip("/")

    @property
    def api_key(self) -> str:
        return self.get("api_key", "")

    @property
    def model(self) -> str:
        return self.get("model", "claude-3-7-sonnet-20250219")

    @property
    def telegram_token(self) -> str:
        return self.get("telegram_token", "")

    @property
    def allowed_telegram_users(self) -> List[int]:
        users = self.get("allowed_telegram_users", [])
        return [int(u) for u in users if str(u).strip()]

    @property
    def device_name(self) -> str:
        return self.get("device_name", "Android-Node")

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.model)


def fetch_available_models(endpoint: str, api_key: str, timeout: int = 8) -> List[str]:
    """Queries GET /v1/models to fetch list of available models from the provider."""
    clean_endpoint = endpoint.rstrip("/")
    models_url = f"{clean_endpoint}/models" if not clean_endpoint.endswith("/models") else clean_endpoint
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "ArtificialAnamika/1.0",
        "Accept": "application/json"
    }

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(models_url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = []
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                for item in data["data"]:
                    if isinstance(item, dict) and "id" in item:
                        models.append(item["id"])
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "id" in item:
                        models.append(item["id"])
                    elif isinstance(item, str):
                        models.append(item)
            return sorted(list(set(models)))
    except Exception:
        return []


def interactive_model_selector(available_models: List[str], default_model: str = "") -> str:
    """Rich interactive model selector with pagination, keyword search, and numbered selection."""
    if not available_models:
        return default_model

    # Prioritize Claude, GPT-4, DeepSeek, Llama
    def model_priority(m: str) -> int:
        m_low = m.lower()
        if "claude-3-7" in m_low or "claude-3.7" in m_low or "sonnet-4" in m_low:
            return 0
        if "claude-3-5" in m_low or "claude-3.5" in m_low or "sonnet" in m_low:
            return 1
        if "gpt-4o" in m_low or "o3" in m_low or "o1" in m_low:
            return 2
        if "deepseek" in m_low:
            return 3
        if "llama-3" in m_low:
            return 4
        return 10

    sorted_models = sorted(available_models, key=lambda x: (model_priority(x), x))
    current_filter = ""
    page = 0
    page_size = 15

    while True:
        if current_filter:
            filtered = [m for m in sorted_models if current_filter.lower() in m.lower()]
        else:
            filtered = sorted_models

        if not filtered:
            print(f"\n⚠️ No models matched filter '{current_filter}'.")
            reset_choice = input("Press Enter to clear search filter or type new search: ").strip()
            if reset_choice.startswith("/"):
                current_filter = reset_choice[1:].strip()
            elif reset_choice:
                current_filter = reset_choice
            else:
                current_filter = ""
            page = 0
            continue

        total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))

        start_idx = page * page_size
        end_idx = min(start_idx + page_size, len(filtered))
        current_slice = filtered[start_idx:end_idx]

        filter_tag = f" matching '{current_filter}'" if current_filter else ""
        print(f"\n📊 AVAILABLE MODELS ({len(filtered)} total{filter_tag} — Page {page + 1}/{total_pages}):")
        print("-" * 65)

        for i, m in enumerate(current_slice, start=start_idx + 1):
            is_default = " \033[1;32m(Default)\033[0m" if m == default_model else ""
            print(f"  [{i}] {m}{is_default}")

        print("-" * 65)
        print("💡 [Number] Select | [n] Next | [p] Prev | [/query] Search | [all] Show All")

        user_inp = input("\nSelect model > ").strip()

        if not user_inp:
            if default_model and default_model in sorted_models:
                return default_model
            return filtered[0] if filtered else default_model

        # If user picked a number
        if user_inp.isdigit():
            val = int(user_inp)
            if 1 <= val <= len(filtered):
                return filtered[val - 1]
            else:
                print(f"⚠️ Invalid number {val}. Please enter a number between 1 and {len(filtered)}.")
                continue

        low_inp = user_inp.lower()
        if low_inp in ("n", "next"):
            if page < total_pages - 1:
                page += 1
            else:
                print("ℹ️ You are on the last page.")
            continue
        elif low_inp in ("p", "prev", "previous"):
            if page > 0:
                page -= 1
            else:
                print("ℹ️ You are on the first page.")
            continue
        elif low_inp == "all":
            page_size = max(50, len(filtered))
            page = 0
            continue
        elif low_inp.startswith("/") or low_inp.startswith("find ") or low_inp.startswith("search "):
            q = user_inp[1:].strip() if low_inp.startswith("/") else user_inp.split(maxsplit=1)[1].strip()
            current_filter = q
            page = 0
            continue
        elif low_inp in ("clear", "reset"):
            current_filter = ""
            page = 0
            continue
        else:
            # User typed custom or exact model name directly
            return user_inp


def run_setup_wizard(config_path: str = DEFAULT_CONFIG_PATH) -> Config:
    """Interactive CLI setup wizard to configure Endpoint, API Key, Model & Telegram."""
    cfg = Config(config_path)

    print("\n\033[1;36m╔══════════════════════════════════════════════╗")
    print("║   ✨ ARTIFICIAL ANAMIKA — SETUP WIZARD       ║")
    print("║   Autonomous Android OS AI Employee          ║")
    print("╚══════════════════════════════════════════════╝\033[0m\n")

    # Step 1: Endpoint selection
    print("📌 STEP 1: SELECT OR ENTER LLM ENDPOINT URL")
    for i, preset in enumerate(DEFAULT_PRESETS, start=1):
        if preset["url"]:
            print(f"  [{i}] {preset['name']} ({preset['url']})")
        else:
            print(f"  [{i}] {preset['name']}")

    current_endpoint = cfg.get("endpoint", "")
    if current_endpoint:
        print(f"\n  (Current Config: {current_endpoint})")

    choice = input("\nSelect an option [1-6] or press Enter to keep current: ").strip()
    selected_endpoint = ""
    selected_default_model = ""

    if choice.isdigit() and 1 <= int(choice) <= len(DEFAULT_PRESETS):
        idx = int(choice) - 1
        preset = DEFAULT_PRESETS[idx]
        if preset["url"]:
            selected_endpoint = preset["url"]
            selected_default_model = preset["default_model"]
        else:
            selected_endpoint = input("Enter custom Endpoint URL (e.g. http://192.168.1.50:8000/v1): ").strip()
    elif not choice and current_endpoint:
        selected_endpoint = current_endpoint
    else:
        if choice.startswith("http://") or choice.startswith("https://"):
            selected_endpoint = choice
        else:
            selected_endpoint = "https://api.mandalworkforce.com/v1"

    # Step 2: API Key
    print("\n" + "-" * 60)
    print("📌 STEP 2: ENTER API KEY")
    current_key = cfg.get("api_key", "")
    masked_key = f"{current_key[:6]}...{current_key[-4:]}" if len(current_key) > 10 else ("Set" if current_key else "Not set")
    
    key_prompt = f"Enter API Key [Current: {masked_key}]: " if current_key else "Enter API Key: "
    input_key = input(key_prompt).strip()
    selected_key = input_key if input_key else current_key

    # Step 3: Model Selection & Dynamic Fetch with Pagination & Search
    print("\n" + "-" * 60)
    print("📌 STEP 3: MODEL SELECTION")
    print(f"🔍 Probing endpoint '{selected_endpoint}' for available models...")

    available_models = fetch_available_models(selected_endpoint, selected_key)
    current_model = cfg.get("model", selected_default_model or "claude-3-7-sonnet-20250219")

    if available_models:
        print(f"✅ Successfully fetched {len(available_models)} models from provider.")
        selected_model = interactive_model_selector(available_models, default_model=current_model)
    else:
        print("⚠️ Could not auto-fetch models list (Endpoint might restrict /v1/models).")
        m_input = input(f"Enter Model Name [Default: {current_model}]: ").strip()
        selected_model = m_input if m_input else current_model

    # Step 4: Device & Telegram Settings
    print("\n" + "-" * 60)
    print("📌 STEP 4: TELEGRAM BOT INTEGRATION (OPTIONAL FOR BACKGROUND 24x7)")
    cur_tg = cfg.get("telegram_token", "")
    tg_prompt = f"Enter Telegram Bot Token (leave empty to skip) [Current: {'Set' if cur_tg else 'None'}]: "
    tg_token = input(tg_prompt).strip()
    if not tg_token and cur_tg:
        tg_token = cur_tg

    allowed_users = cfg.get("allowed_telegram_users", [])
    if tg_token:
        cur_users_str = ",".join(str(u) for u in allowed_users)
        u_prompt = f"Enter Allowed Telegram User ID(s) comma-separated [Current: {cur_users_str or 'None'}]: "
        users_input = input(u_prompt).strip()
        if users_input:
            allowed_users = [int(u.strip()) for u in users_input.split(",") if u.strip().isdigit()]

    # Step 5: Device Name
    cur_device = cfg.get("device_name", "OnePlus-Tab")
    d_input = input(f"Enter Device Identifier Name [Default: {cur_device}]: ").strip()
    device_name = d_input if d_input else cur_device

    # Save to config
    cfg.set("endpoint", selected_endpoint)
    cfg.set("api_key", selected_key)
    cfg.set("model", selected_model)
    cfg.set("telegram_token", tg_token)
    cfg.set("allowed_telegram_users", allowed_users)
    cfg.set("device_name", device_name)
    cfg.set("language_preference", "hinglish")

    print("\n" + "=" * 60)
    print("✅ CONFIGURATION SAVED SUCCESSFULLY!")
    print(f"  • Endpoint: {selected_endpoint}")
    print(f"  • Model:    {selected_model}")
    print(f"  • Device:   {device_name}")
    print(f"  • Telegram: {'Configured' if tg_token else 'Disabled (CLI only)'}")
    print(f"  • File:     {cfg.config_path}")
    print("=" * 60 + "\n")

    return cfg
