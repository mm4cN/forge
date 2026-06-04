import typer

from rich.console import Console

from forge.config import load_config, set_default_model, set_model_provider
from forge.providers.factory import get_provider, list_providers

app = typer.Typer(help="Manage model providers")
console = Console()


@app.command("list")
def model_list() -> None:
    """
    List available models for current provider.
    """
    models = get_provider().list_models()

    if not models:
        console.print("[yellow]No models found.[/yellow]")
        return

    current = load_config()["default_model"]

    for model in models:
        marker = "*" if model == current else " "
        console.print(f"{marker} {model}")


@app.command("get")
def model_get() -> None:
    """
    Show current default model.
    """
    config = load_config()
    console.print(config["default_model"])


@app.command("set")
def model_set(model: str) -> None:
    """
    Set default model.
    """
    set_default_model(model)
    console.print(f"[green]Default model set:[/green] {model}")


@app.command("providers")
def model_providers() -> None:
    """
    List available model providers.
    """
    current = load_config().get("provider", "ollama")

    for provider in list_providers():
        marker = "*" if provider == current else " "
        console.print(f"{marker} {provider}")


@app.command("use")
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

    set_model_provider(provider=provider, model=model)

    console.print(f"[green]Provider:[/green] {provider}")
    console.print(f"[green]Default model:[/green] {model}")
