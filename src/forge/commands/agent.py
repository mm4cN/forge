import typer

from rich.console import Console

from forge.db import add_message, connect, create_session, get_messages, add_model_call
from forge.config import load_config
from forge.providers.factory import get_provider
from forge.runtime import run_agent
from forge.workspace import get_workspace

app = typer.Typer()
console = Console()


def print_footer(
    model: str,
    session: str,
) -> None:
    console.print(f"[dim]model: {model}[/dim]")
    console.print(f"[dim]session: {session}[/dim]")
    console.print(f"[dim]workspace: {get_workspace()}[/dim]")


def ensure_session(
    conn,
    session: str | None,
    title: str,
) -> str:
    if session is not None:
        return session

    return create_session(conn, title=title[:64])


@app.command()
def ask(
    prompt: str,
    model: str | None = typer.Option(None, "--model", "-m"),
    session: str | None = typer.Option(None, "--session", "-s"),
) -> None:
    """
    Ask the model once without tool execution.
    """
    conn = connect()
    config = load_config()
    selected_model = model or config["default_model"]
    session = ensure_session(conn, session, prompt)

    add_message(conn, session, "user", prompt)
    messages = get_messages(conn, session)

    provider = get_provider()

    try:
        model_response = provider.chat(selected_model, messages)
    except RuntimeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    answer = model_response.text

    add_model_call(
        conn=conn,
        session_id=session,
        provider=provider.name,
        model=selected_model,
        prompt_tokens=model_response.prompt_tokens,
        completion_tokens=model_response.completion_tokens,
        total_tokens=model_response.total_tokens,
        duration_ms=model_response.duration_ms,
    )

    add_message(conn, session, "assistant", answer)

    console.print()
    console.print(answer)
    console.print()
    print_footer(selected_model, session)


@app.command()
def agent(
    prompt: str,
    model: str | None = typer.Option(None, "--model", "-m"),
    session: str | None = typer.Option(None, "--session", "-s"),
) -> None:
    """
    Run Forge agent with tool execution.
    """
    conn = connect()
    config = load_config()
    selected_model = model or config["default_model"]
    session = ensure_session(conn, session, prompt)

    add_message(conn, session, "user", prompt)
    messages = get_messages(conn, session)

    try:
        answer = run_agent(
            selected_model,
            messages,
            session_id=session,
            conn=conn,
        )
    except RuntimeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1)

    add_message(conn, session, "assistant", answer)

    console.print()
    console.print(answer)
    console.print()
    print_footer(selected_model, session)


@app.command()
def chat(
    model: str | None = typer.Option(None, "--model", "-m"),
    session: str | None = typer.Option(None, "--session", "-s"),
) -> None:
    """
    Start or resume an interactive agent chat session.
    """
    conn = connect()
    config = load_config()
    selected_model = model or config["default_model"]

    if session is None:
        session = create_session(conn, title="Interactive Chat")
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

        add_message(conn, session, "user", prompt)
        messages = get_messages(conn, session)

        try:
            answer = run_agent(
                selected_model,
                messages,
                session_id=session,
                conn=conn,
            )
        except RuntimeError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            continue

        add_message(conn, session, "assistant", answer)

        console.print()
        console.print(f"[bold green]Forge:[/bold green]\n{answer}")
        console.print()
