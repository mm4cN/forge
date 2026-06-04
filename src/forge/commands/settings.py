import typer

from rich.console import Console
from rich.table import Table

from forge.config import load_config, set_approval_mode

console = Console()


def register_config_commands(app: typer.Typer) -> None:
    @app.command()
    def settings() -> None:
        """
        Show configuration.
        """
        cfg = load_config()

        table = Table(title="Forge Settings")
        table.add_column("Key")
        table.add_column("Value")

        for key, value in cfg.items():
            table.add_row(
                str(key),
                str(value),
            )

        console.print(table)

    @app.command("approval")
    def approval(
        enabled: bool,
    ) -> None:
        """
        Enable or disable approval mode.
        """
        set_approval_mode(enabled)

        state = "enabled" if enabled else "disabled"
        console.print(f"[green]Approval mode {state}[/green]")
