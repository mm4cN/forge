from rich.console import Console
from rich.syntax import Syntax

from forge.approval_preview import build_approval_preview

console = Console()

APPROVAL_REQUIRED_TOOLS = {
    "run_command",
    "write_file",
    "replace_in_file",
    "edit_file",
}


def requires_approval(tool_name: str) -> bool:
    return tool_name in APPROVAL_REQUIRED_TOOLS


def ask_for_approval(
    tool_name: str,
    arguments: dict,
) -> bool:
    console.print()
    console.print(f"[bold yellow]Tool approval required:[/bold yellow] {tool_name}")

    preview = build_approval_preview(
        tool_name,
        arguments,
    )

    console.print(
        Syntax(
            preview.content,
            preview.lexer,
            line_numbers=True,
            word_wrap=True,
        )
    )

    if not preview.requires_approval:
        console.print("[dim]No changes detected. Skipping approval.[/dim]")
        return True

    answer = console.input("Approve? (y/N): ")

    return answer.strip().lower() in {"y", "yes"}
