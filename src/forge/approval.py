from rich.console import Console
from rich.syntax import Syntax

console = Console()

APPROVAL_REQUIRED_TOOLS = {
    "run_command",
    "write_file",
    "replace_in_file",
}


def requires_approval(tool_name: str) -> bool:
    return tool_name in APPROVAL_REQUIRED_TOOLS


def ask_for_approval(
    tool_name: str,
    arguments: dict,
) -> bool:
    console.print()
    console.print(f"[bold yellow]Tool approval required:[/bold yellow] {tool_name}")

    rendered = repr(arguments)

    console.print(
        Syntax(
            rendered,
            "python",
            theme="monokai",
            line_numbers=False,
            word_wrap=True,
        )
    )

    answer = console.input("Approve? (y/N): ")

    return answer.strip().lower() in {"y", "yes"}
