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

    save_config(DEFAULT_CONFIG)


def load_config() -> dict:
    ensure_config()

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)

    return DEFAULT_CONFIG | data


def save_config(config: dict) -> None:
    ensure_app_dirs()

    content = "\n".join(
        f'{key} = "{value}"'
        for key, value in config.items()
    )

    CONFIG_PATH.write_text(
        content + "\n",
        encoding="utf-8",
    )


def set_default_model(model: str) -> None:
    config = load_config()
    config["default_model"] = model
    save_config(config)
