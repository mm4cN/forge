from rich.console import Console

from forge.metrics import tokens_per_second
from forge.workspace import get_workspace

console = Console()


def print_footer(
    model: str,
    session: str | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    total_tokens: int | None = None,
    duration_ms: int | None = None,
    show_workspace: bool = True,
    steps: int | None = None,
) -> None:
    console.print(f"[dim]model: {model}[/dim]")

    if session is not None:
        console.print(f"[dim]session: {session}[/dim]")

    if show_workspace:
        console.print(f"[dim]workspace: {get_workspace()}[/dim]")

    if duration_ms is not None:
        console.print(f"[dim]duration: {duration_ms} ms[/dim]")

    tps = tokens_per_second(
        completion_tokens,
        duration_ms,
    )
    if (
        prompt_tokens is not None
        or completion_tokens is not None
        or total_tokens is not None
    ):
        console.print(
            "[dim]"
            f"tokens: input={prompt_tokens or '-'}, "
            f"output={completion_tokens or '-'}, "
            f"total={total_tokens or '-'}, "
            f"steps={steps}"
            "[/dim]"
        )

    if tps is not None:
        console.print(f"[dim]throughput: {tps:.1f} tok/s[/dim]")
