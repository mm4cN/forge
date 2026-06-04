import typer

from rich.console import Console
from rich.table import Table

from forge.db import connect, get_messages, list_sessions

console = Console()


def register_session_commands(app: typer.Typer) -> None:
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
        messages = get_messages(conn, session)

        for message in messages:
            role = message["role"]
            content = message["content"]

            if role == "user":
                console.print(f"\n[bold cyan]You:[/bold cyan]\n{content}")
            else:
                console.print(f"\n[bold green]Forge:[/bold green]\n{content}")
