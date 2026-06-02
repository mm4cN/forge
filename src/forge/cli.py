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
from forge.ollama import chat

app = typer.Typer(help="Forge — local LLM CLI")
console = Console()


@app.command()
def ask(
    prompt: str,
    model: str | None = typer.Option(None, "--model", "-m"),
    session: str | None = typer.Option(None, "--session", "-s"),
) -> None:
    """
    Ask the local model a question.
    """
    conn = connect()
    config = load_config()

    selected_model = model or config["default_model"]

    if session is None:
        session = create_session(conn, title=prompt[:64])

    add_message(conn, session, "user", prompt)

    messages = get_messages(conn, session)
    answer = chat(selected_model, messages)

    add_message(conn, session, "assistant", answer)

    console.print()
    console.print(answer)
    console.print()
    console.print(f"[dim]model: {selected_model}[/dim]")
    console.print(f"[dim]session: {session}[/dim]")


@app.command()
def sessions() -> None:
    """
    List saved sessions.
    """
    conn = connect()
    rows = list_sessions(conn)

    table = Table(title="Forge sessions")
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
def history(session: str) -> None:
    """
    Show session history.
    """
    conn = connect()
    messages = get_messages(conn, session)

    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            console.print(f"\n[bold cyan]You:[/bold cyan]\n{content}")
        else:
            console.print(f"\n[bold green]Forge:[/bold green]\n{content}")


@app.command()
def config() -> None:
    """
    Show active Forge config.
    """
    cfg = load_config()

    table = Table(title="Forge config")
    table.add_column("Key")
    table.add_column("Value")

    for key, value in cfg.items():
        table.add_row(str(key), str(value))

    console.print(table)
