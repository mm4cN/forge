import os
import time

import requests

from forge.providers.base import ModelInfo, ModelProvider, ModelResponse


OPENROUTER_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider(ModelProvider):
    @property
    def name(self) -> str:
        return "openrouter"

    def __init__(self) -> None:
        self.api_key = os.environ.get("OPENROUTER_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. "
                "Export it first, e.g. export OPENROUTER_API_KEY='...'"
            )

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> ModelResponse:
        started_at = time.perf_counter()

        response = requests.post(
            f"{OPENROUTER_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.2,
            },
            timeout=120,
        )

        if response.status_code >= 400:
            raise RuntimeError(
                f"OpenRouter request failed: {response.status_code}\n"
                f"{response.text}"
            )

        data = response.json()
        duration_ms = int((time.perf_counter() - started_at) * 1000)

        usage = data.get("usage", {})

        return ModelResponse(
            text=data["choices"][0]["message"]["content"],
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            duration_ms=duration_ms,
        )

    def list_models(self) -> list[str]:
        response = requests.get(
            f"{OPENROUTER_URL}/models",
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            timeout=30,
        )

        if response.status_code >= 400:
            raise RuntimeError(
                f"OpenRouter model list failed: {response.status_code}\n"
                f"{response.text}"
            )

        data = response.json()

        return sorted(
            model["id"]
            for model in data.get("data", [])
            if isinstance(model.get("id"), str)
        )

    def get_model_info(
        self,
        model: str,
    ) -> ModelInfo:
        response = requests.get(
            f"{OPENROUTER_URL}/models",
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            timeout=30,
        )

        if response.status_code >= 400:
            return ModelInfo(context_window=4096)

        data = response.json()

        for item in data.get("data", []):
            if item.get("id") == model:
                return ModelInfo(
                    context_window=item.get("context_length") or 4096,
                )

        return ModelInfo(context_window=4096)
