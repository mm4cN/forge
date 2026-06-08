from forge.providers.base import ModelResponse
from forge.providers.factory import get_provider
from forge.tools.read_file import read_file


REVIEW_PROMPT = """Review the following code changes.

Focus only on potential issues:
- bugs
- regressions
- incorrect behavior
- maintainability problems
- missing tests
- risky assumptions

Do not report missing tests unless the diff changes application logic, error handling, data persistence, or public behavior.

Do not report possible None errors if the code explicitly checks for None.

If the only possible findings are generic test requests, unused imports, or speculative risks, return:
"No significant issues found."

Return concise Markdown.
"""

MAX_FILE_SIZE = 5000
MAX_FILE_LINES = 300


def build_review_context(
    files: list[str],
) -> str:
    chunks: list[str] = []

    for path in files:
        try:
            content = read_file(
                path=path,
                start_line=1,
                max_lines=MAX_FILE_LINES,
            )
        except Exception:
            continue

        if len(content) > MAX_FILE_SIZE:
            content = content[:MAX_FILE_SIZE] + "\n...<truncated>"

        chunks.append(f"File: {path}\n\n{content}")

    return "\n\n".join(chunks)


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

    context = ""
    if files:
        context = build_review_context(files)

    content = f"""
    {REVIEW_PROMPT}

    Diff:

    {diff}
    """

    if context:
        content += f"""

    Changed files:

    {context}
    """

    messages = [
        {
            "role": "user",
            "content": content,
        }
    ]

    return provider.chat(
        model,
        messages,
    )
