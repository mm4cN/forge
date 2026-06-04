from abc import ABC, abstractmethod


class ModelProvider(ABC):
    @abstractmethod
    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> str:
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        pass
