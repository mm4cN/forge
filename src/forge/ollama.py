import subprocess
import time

import requests

from forge.config import load_config


def ollama_url() -> str:
    return load_config()["ollama_url"]


def is_running() -> bool:
    try:
        response = requests.get(ollama_url(), timeout=1)
        return response.status_code == 200
    except requests.RequestException:
        return False


def ensure_running() -> None:
    if is_running():
        return

    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    for _ in range(30):
        if is_running():
            return
        time.sleep(0.2)

    raise RuntimeError("Ollama nie wstała. Demon siedzi w kącie i kontempluje SIGTERM.")


def chat(model: str, messages: list[dict[str, str]]) -> str:
    ensure_running()

    response = requests.post(
        f"{ollama_url()}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()

    return response.json()["message"]["content"]
