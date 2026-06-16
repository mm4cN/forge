import json
import typer
import subprocess

from rich.console import Console

from forge.config import load_config
from forge.output import print_footer
from forge.review import review_diff
from forge.tools.git_diff import git_diff

app = typer.Typer()
console = Console()


def extract_review_text(text: str) -> str:
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            response = data.get("response")
            if isinstance(response, str):
                return response
    except Exception:
        pass

    return text


@app.command()
def review(
    model: str | None = typer.Option(None, "--model", "-m"),
) -> None:
    """
    Review current git diff.
    """
    config = load_config()
    selected_model = model or config["default_model"]

    diff = git_diff()
    changed_files = (
        subprocess.check_output(
            ["git", "diff", "--name-only"],
            text=True,
        )
        .strip()
        .splitlines()
    )

    try:
        response = review_diff(
            model=selected_model,
            diff=diff,
            files=changed_files,
        )
    except RuntimeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    console.print()
    console.print(extract_review_text(response.text))
    console.print()

    print_footer(
        selected_model,
        total_tokens=response.total_tokens,
        duration_ms=response.duration_ms,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
    )
