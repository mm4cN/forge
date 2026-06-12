import typer

from rich.console import Console
from rich.table import Table

from forge.db import connect, get_project_by_workspace
from forge.project_memory import sync_project_memory
from forge.workspace import get_workspace

app = typer.Typer()
console = Console()


PROJECT_TEMPLATE = """# Project

## Overview

Describe this project.

## Rules

- Use type hints.
- Prefer small, focused changes.
- Prefer workspace-relative paths.
- Run formatting and checks when appropriate.

## Build and Test

Describe how to build and test this project.
"""


@app.command()
def init(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing .forge/project.md",
    ),
) -> None:
    """
    Create .forge/project.md.
    """
    workspace = get_workspace()
    forge_dir = workspace / ".forge"
    project_md = forge_dir / "project.md"

    forge_dir.mkdir(parents=True, exist_ok=True)

    if project_md.exists() and not force:
        console.print(f"[yellow]Already exists:[/yellow] {project_md}")
        return

    project_md.write_text(
        PROJECT_TEMPLATE,
        encoding="utf-8",
    )

    console.print(f"[green]Created:[/green] {project_md}")


@app.command()
def project() -> None:
    """
    Show current project memory status.
    """
    conn = connect()
    memory = sync_project_memory(conn)

    if memory is not None:
        table = Table(title="Forge Project")
        table.add_column("Key")
        table.add_column("Value")

        table.add_row("Name", memory.name)
        table.add_row("Workspace", memory.workspace_path)
        table.add_row("Git remote", memory.git_remote or "-")
        table.add_row("project.md", memory.project_md_path)
        table.add_row("SHA256", memory.project_md_sha256)

        console.print(table)
        return

    workspace = get_workspace()
    row = get_project_by_workspace(
        conn,
        str(workspace),
    )

    if row is None:
        console.print("[yellow]No .forge/project.md found.[/yellow]")
        console.print("Run: forge init")
        return

    table = Table(title="Forge Project")
    table.add_column("Key")
    table.add_column("Value")

    table.add_row("Name", row["name"])
    table.add_row("Workspace", row["workspace_path"])
    table.add_row("Git remote", row["git_remote"] or "-")
    table.add_row("project.md", row["project_md_path"])
    table.add_row("SHA256", row["project_md_sha256"])
    table.add_row("Updated", row["updated_at"])

    console.print(table)


@app.command("project-sync")
def project_sync() -> None:
    """
    Sync .forge/project.md into the local database.
    """
    conn = connect()
    memory = sync_project_memory(conn)

    if memory is None:
        console.print("[yellow]No .forge/project.md found.[/yellow]")
        return

    console.print(f"[green]Synced project:[/green] {memory.name}")
    console.print(f"[dim]workspace: {memory.workspace_path}[/dim]")
    console.print(f"[dim]sha256: {memory.project_md_sha256}[/dim]")
