import typer

from rich.console import Console
from rich.table import Table

from forge.config import load_config
from forge.db import (
    add_message,
    connect,
    create_session,
    get_messages,
    list_sessions,
)
from forge.runtime import run_agent
from forge.workspace import get_workspace

app = typer.Typer(help="Forge — local coding agent")

console = Console()


@app.command()
def ask(
    prompt: str,
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="Model to use",
    ),
    session: str | None = typer.Option(
        None,
        "--session",
        "-s",
        help="Session ID",
    ),
) -> None:
    """
    Ask Forge to perform a task.
    """
    conn = connect()

    config = load_config()

    selected_model = model or config["default_model"]

    if session is None:
        session = create_session(
            conn,
            title=prompt[:64],
        )

    add_message(
        conn,
        session,
        "user",
        prompt,
    )

    messages = get_messages(conn, session)

    answer = run_agent(
        selected_model,
        messages,
    )

    add_message(
        conn,
        session,
        "assistant",
        answer,
    )

    console.print()
    console.print(answer)
    console.print()

    console.print(f"[dim]model: {selected_model}[/dim]")
    console.print(f"[dim]session: {session}[/dim]")
    console.print(f"[dim]workspace: {get_workspace()}[/dim]")


@app.command()
def sessions() -> None:
    """
    List sessions.
    """
    conn = connect()

    rows = list_sessions(conn)

    table = Table(title="Forge Sessions")

    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Created")

    for row in rows:
        table.add_row(
            row["id"],
            row["title"],
            row["created_at"],
        )

    console.print(table)


@app.command()
def history(
    session: str,
) -> None:
    """
    Show session history.
    """
    conn = connect()

    messages = get_messages(
        conn,
        session,
    )

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            console.print(
                f"\n[bold cyan]You:[/bold cyan]\n{content}"
            )
        else:
            console.print(
                f"\n[bold green]Forge:[/bold green]\n{content}"
            )


@app.command()
def config() -> None:
    """
    Show configuration.
    """
    cfg = load_config()

    table = Table(title="Forge Config")

    table.add_column("Key")
    table.add_column("Value")

    for key, value in cfg.items():
        table.add_row(
            str(key),
            str(value),
        )

    console.print(table)

@app.command()
def workspace() -> None:
    """
    Show current workspace.
    """
    console.print(get_workspace())
