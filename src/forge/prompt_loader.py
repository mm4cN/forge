from importlib.resources import files
from typing import Literal

PromptContext = Literal["ask", "agent", "review"]


def load_prompt(name: str) -> str:
    return files("forge.prompts").joinpath(name).read_text(encoding="utf-8")


def build_system_prompt(
    context: PromptContext,
) -> str:
    prompt_files = {
        "ask": [
            "ask.md",
        ],
        "agent": [
            "system.md",
            "coding.md",
            "tools.md",
            "workflow.md",
            "project_analysis.md",
        ],
        "review": [
            "review.md",
        ],
    }

    return "\n\n".join(load_prompt(name) for name in prompt_files[context])
