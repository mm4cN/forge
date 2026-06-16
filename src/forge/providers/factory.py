from collections.abc import Callable

from forge.config import load_config
from forge.providers.base import ModelProvider
from forge.providers.gemini import GeminiProvider
from forge.providers.ollama import OllamaProvider
from forge.providers.openrouter import OpenRouterProvider


ProviderFactory = Callable[[], ModelProvider]


PROVIDERS: dict[str, ProviderFactory] = {
    "ollama": OllamaProvider,
    "gemini": GeminiProvider,
    "openrouter": OpenRouterProvider,
}


def get_provider() -> ModelProvider:
    config = load_config()
    provider_name = config.get("provider", "ollama")

    try:
        provider_factory = PROVIDERS[provider_name]
    except KeyError as exc:
        available = ", ".join(sorted(PROVIDERS))

        raise ValueError(
            f"Unknown model provider: {provider_name}. Available providers: {available}"
        ) from exc

    return provider_factory()


def list_providers() -> list[str]:
    return sorted(PROVIDERS)
