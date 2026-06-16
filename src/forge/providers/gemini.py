import os
import requests

from forge.providers.base import ModelProvider, ModelResponse, ModelInfo
from requests import HTTPError
import time


class GeminiProvider(ModelProvider):
    @property
    def name(self) -> str:
        return "gemini"

    def __init__(self) -> None:
        self.api_key = os.environ.get("GEMINI_AUTH_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_AUTH_KEY is not set. "
                "Export it first, e.g. export GEMINI_AUTH_KEY='...'"
            )

    def __raise_for_status(self, response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except HTTPError as exc:
            try:
                payload = response.json()
                message = payload.get("error", {}).get("message", str(exc))
                status = payload.get("error", {}).get("status", "unknown")
            except ValueError:
                message = response.text
                status = "unknown"

            if response.status_code == 429:
                raise RuntimeError(
                    "Gemini API rate limit exceeded.\n\n"
                    f"Status: {status}\n"
                    f"Message: {message}\n\n"
                    "Try one of:\n"
                    "- wait for the quota window to reset\n"
                    "- switch to another Gemini model\n"
                    "- switch back to Ollama\n"
                    "- use a model with higher free-tier limits"
                ) from exc

            if response.status_code == 403:
                raise RuntimeError(
                    "Gemini API access denied.\n\n"
                    f"Status: {status}\n"
                    f"Message: {message}\n\n"
                    "This model may require billing or may not be available for your project."
                ) from exc

            raise RuntimeError(
                "Gemini API request failed.\n\n"
                f"HTTP status: {response.status_code}\n"
                f"Status: {status}\n"
                f"Message: {message}"
            ) from exc

    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> ModelResponse:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{model}:generateContent"
        )

        payload = {
            "systemInstruction": self._build_system_instruction(messages),
            "contents": self._build_contents(messages),
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192,
            },
        }

        started_at = time.perf_counter()
        response = requests.post(
            url,
            params={"key": self.api_key},
            json=payload,
            timeout=120,
        )
        self.__raise_for_status(response)

        data = response.json()
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        usage = data.get("usageMetadata", {})

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Invalid Gemini response: {data}") from exc

        return ModelResponse(
            text=text,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            total_tokens=usage.get("totalTokenCount"),
            duration_ms=duration_ms,
        )

    def list_models(self) -> list[str]:
        url = "https://generativelanguage.googleapis.com/v1beta/models"

        response = requests.get(
            url,
            params={"key": self.api_key},
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        models: list[str] = []

        for model in data.get("models", []):
            name = model.get("name", "")

            if not name.startswith("models/"):
                continue

            model_name = name.removeprefix("models/")

            methods = model.get("supportedGenerationMethods", [])

            if "generateContent" in methods:
                models.append(model_name)

        return sorted(models)

    def _build_system_instruction(
        self,
        messages: list[dict[str, str]],
    ) -> dict | None:
        system_parts = [
            message["content"] for message in messages if message["role"] == "system"
        ]

        if not system_parts:
            return None

        return {
            "parts": [
                {
                    "text": "\n\n".join(system_parts),
                }
            ]
        }

    def _build_contents(
        self,
        messages: list[dict[str, str]],
    ) -> list[dict]:
        contents: list[dict] = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "system":
                continue

            gemini_role = "model" if role == "assistant" else "user"

            contents.append(
                {
                    "role": gemini_role,
                    "parts": [
                        {
                            "text": content,
                        }
                    ],
                }
            )

        return contents

    def get_model_info(
        self,
        model: str,
    ) -> ModelInfo:
        return ModelInfo(
            context_window=1_000_000,
            max_tool_results_chars=4_000,
        )
