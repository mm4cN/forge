import subprocess
import time

import requests

from forge.config import load_config
from forge.providers.base import ModelProvider, ModelResponse


class OllamaProvider(ModelProvider):
    def __init__(self) -> None:
        self.config = load_config()

    def ollama_url(self) -> str:
        return self.config["ollama_url"]

    def is_running(self) -> bool:
        try:
            response = requests.get(
                self.ollama_url(),
                timeout=1,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def ensure_running(self) -> None:
        if self.is_running():
            return

        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        for _ in range(30):
            if self.is_running():
                return
            time.sleep(0.2)

        raise RuntimeError("Ollama did not start.")

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> ModelResponse:
        self.ensure_running()

        response = requests.post(
            f"{self.ollama_url()}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 4096,
                },
            },
            timeout=120,
        )
        response.raise_for_status()

        data = response.json()

        return ModelResponse(
            text=data["message"]["content"],
        )

    def list_models(self) -> list[str]:
        self.ensure_running()

        response = requests.get(
            f"{self.ollama_url()}/api/tags",
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()

        return [model["name"] for model in data.get("models", [])]
