from rich.console import Console

from forge.metrics import tokens_per_second
from forge.workspace import get_workspace

console = Console()


def print_footer(
    model: str,
    session: str | None = None,
    total_tokens: int | None = None,
    duration_ms: int | None = None,
    show_workspace: bool = True,
) -> None:
    console.print(f"[dim]model: {model}[/dim]")

    if session is not None:
        console.print(f"[dim]session: {session}[/dim]")

    if show_workspace:
        console.print(f"[dim]workspace: {get_workspace()}[/dim]")

    if duration_ms is not None:
        console.print(f"[dim]duration: {duration_ms} ms[/dim]")

    tps = tokens_per_second(
        total_tokens,
        duration_ms,
    )

    if tps is not None:
        console.print(f"[dim]throughput: {tps:.1f} tok/s[/dim]")
