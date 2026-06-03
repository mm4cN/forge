from pathlib import Path
import tomllib

APP_DIR = Path.home() / ".forge"
CONFIG_PATH = APP_DIR / "config.toml"
DB_PATH = APP_DIR / "forge.db"
LOG_DIR = APP_DIR / "logs"
SESSIONS_DIR = APP_DIR / "sessions"

DEFAULT_CONFIG = {
    "ollama_url": "http://127.0.0.1:11434",
    "default_model": "qwen2.5-coder:7b",
}


def ensure_app_dirs() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def ensure_config() -> None:
    ensure_app_dirs()

    if CONFIG_PATH.exists():
        return

    CONFIG_PATH.write_text(
        """ollama_url = "http://127.0.0.1:11434"
default_model = "qwen2.5-coder:7b"
""",
        encoding="utf-8",
    )


def load_config() -> dict:
    ensure_config()

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)

    return DEFAULT_CONFIG | data
