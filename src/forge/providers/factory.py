from forge.config import load_config
from forge.providers.base import ModelProvider
from forge.providers.ollama import OllamaProvider


def get_provider() -> ModelProvider:
    config = load_config()
    provider = config.get("provider", "ollama")

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(f"Unknown model provider: {provider}")
