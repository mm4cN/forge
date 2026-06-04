from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ModelResponse:
    text: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    duration_ms: int | None = None


class ModelProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> ModelResponse:
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        pass
