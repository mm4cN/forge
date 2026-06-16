from forge.prompt_loader import build_system_prompt
from forge.providers.base import ModelResponse
from forge.providers.factory import get_provider


def build_review_context(
    files: list[str],
) -> str:
    if not files:
        return ""

    return "Changed files:\n" + "\n".join(f"- {path}" for path in files)


def review_diff(
    model: str,
    diff: str,
    files: list[str] | None = None,
) -> ModelResponse:
    if not diff.strip():
        return ModelResponse(
            text="No changes to review.",
        )

    provider = get_provider()

    content = f"""Diff:

{diff}
"""

    if files:
        context = build_review_context(files)

        if context:
            content += f"""

{context}
"""

    messages = [
        {
            "role": "system",
            "content": build_system_prompt("review"),
        },
        {
            "role": "user",
            "content": content,
        },
    ]

    return provider.chat(
        model,
        messages,
    )
