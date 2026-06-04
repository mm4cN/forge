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

from forge.tools.replace_in_file import replace_in_file
from forge.tools.find_files import find_files
from forge.tools.list_directory import list_directory
from forge.tools.read_file import read_file
from forge.tools.search_in_files import search_in_files
from forge.tools.git_diff import git_diff
from forge.tools.git_status import git_status
from forge.config import load_config, set_default_model, set_model_provider
from forge.providers.factory import get_provider, list_providers
from forge.providers.factory import get_provider
from forge.providers.factory import get_provider, list_providers

app = typer.Typer(help="Forge — local coding agent")
model_app = typer.Typer(help="Manage Ollama models")
app.add_typer(model_app, name="model")

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

    try:
        answer = run_agent(
            selected_model,
            messages,
        )
    except RuntimeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

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

@app.command("ls")
def ls(
    path: str = ".",
) -> None:
    """
    List directory contents.
    """
    console.print(
        list_directory(path=path)
    )

@app.command()
def find(
    pattern: str,
    path: str = ".",
) -> None:
    """
    Find files.
    """
    console.print(
        find_files(
            pattern=pattern,
            path=path,
        )
    )

@app.command()
def search(
    query: str,
    path: str = ".",
) -> None:
    """
    Search text in files.
    """
    console.print(
        search_in_files(
            query=query,
            path=path,
        )
    )

@app.command()
def cat(
    path: str,
    start_line: int = 1,
    max_lines: int = 200,
) -> None:
    """
    Read file.
    """
    console.print(
        read_file(
            path=path,
            start_line=start_line,
            max_lines=max_lines,
        )
    )

@app.command()
def chat(
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
        help="Existing session ID to resume",
    ),
) -> None:
    """
    Start or resume an interactive agent chat session.
    """
    conn = connect()
    config = load_config()

    selected_model = model or config["default_model"]

    if session is None:
        session = create_session(
            conn,
            title="Interactive Chat",
        )
        console.print(f"[green]Started new session:[/green] {session}")
    else:
        console.print(f"[green]Resumed session:[/green] {session}")

    console.print(f"[dim]model: {selected_model}[/dim]")
    console.print(f"[dim]workspace: {get_workspace()}[/dim]")
    console.print("[dim]Type 'exit', 'quit' or Ctrl+C to leave.[/dim]\n")

    while True:
        try:
            prompt = typer.prompt("forge")
        except KeyboardInterrupt:
            console.print("\n[dim]bye[/dim]")
            break

        prompt = prompt.strip()

        if not prompt:
            continue

        if prompt.lower() in {"exit", "quit"}:
            console.print("[dim]bye[/dim]")
            break

        add_message(
            conn,
            session,
            "user",
            prompt,
        )

        messages = get_messages(
            conn,
            session,
        )

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
        console.print(f"[bold green]Forge:[/bold green]\n{answer}")
        console.print()

@app.command()
def status() -> None:
    """
    Show git status.
    """
    console.print(
        git_status()
    )

@app.command()
def diff() -> None:
    """
    Show git diff.
    """
    console.print(
        git_diff()
    )

@app.command()
def replace(
    path: str,
    old: str,
    new: str,
) -> None:
    """
    Replace text in file.
    """
    console.print(
        replace_in_file(
            path=path,
            old=old,
            new=new,
        )
    )

@model_app.command("list")
def model_list() -> None:
    """
    List locally available Ollama models.
    """
    models = get_provider().list_models()

    if not models:
        console.print("[yellow]No local models found.[/yellow]")
        return

    current = load_config()["default_model"]

    for model in models:
        marker = "*" if model == current else " "
        console.print(f"{marker} {model}")


@model_app.command("get")
def model_get() -> None:
    """
    Show current default model.
    """
    config = load_config()
    console.print(config["default_model"])


@model_app.command("set")
def model_set(model: str) -> None:
    """
    Set default model.
    """
    set_default_model(model)
    console.print(f"[green]Default model set:[/green] {model}")

@model_app.command("providers")
def model_providers() -> None:
    """
    List available model providers.
    """
    current = load_config().get("provider", "ollama")

    for provider in list_providers():
        marker = "*" if provider == current else " "
        console.print(f"{marker} {provider}")

@model_app.command("provider-get")
def provider_get() -> None:
    """
    Show current provider.
    """
    config = load_config()

    console.print(
        config.get(
            "provider",
            "ollama",
        )
    )

@model_app.command("use")
def model_use(
    provider: str,
    model: str,
) -> None:
    """
    Set provider and default model.
    """
    available = list_providers()

    if provider not in available:
        console.print(f"[red]Unknown provider:[/red] {provider}")
        console.print(f"Available: {', '.join(available)}")
        raise typer.Exit(1)

    set_model_provider(
        provider=provider,
        model=model,
    )

    console.print(f"[green]Provider:[/green] {provider}")
    console.print(f"[green]Default model:[/green] {model}")
