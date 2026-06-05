import typer
import json

from rich.console import Console
from rich.table import Table

from forge.db import connect, list_model_calls, list_tool_calls

console = Console()


def register_usage_commands(app: typer.Typer) -> None:
    @app.command()
    def usage(
        session: str,
    ) -> None:
        """
        Show model usage for a session.
        """
        conn = connect()
        rows = list_model_calls(conn, session)

        if not rows:
            console.print("[yellow]No model calls found for this session.[/yellow]")
            return

        table = Table(title="Model usage")

        table.add_column("Provider")
        table.add_column("Model")
        table.add_column("Prompt")
        table.add_column("Completion")
        table.add_column("Total")
        table.add_column("Duration")
        table.add_column("Created")

        total_prompt = 0
        total_completion = 0
        total_tokens = 0
        total_duration = 0

        for row in rows:
            prompt_tokens = row["prompt_tokens"] or 0
            completion_tokens = row["completion_tokens"] or 0
            tokens = row["total_tokens"] or 0
            duration_ms = row["duration_ms"] or 0

            total_prompt += prompt_tokens
            total_completion += completion_tokens
            total_tokens += tokens
            total_duration += duration_ms

            table.add_row(
                row["provider"],
                row["model"],
                str(prompt_tokens) if row["prompt_tokens"] is not None else "-",
                str(completion_tokens) if row["completion_tokens"] is not None else "-",
                str(tokens) if row["total_tokens"] is not None else "-",
                f"{duration_ms} ms" if row["duration_ms"] is not None else "-",
                row["created_at"],
            )

        table.add_section()
        table.add_row(
            "TOTAL",
            "",
            str(total_prompt),
            str(total_completion),
            str(total_tokens),
            f"{total_duration} ms",
            "",
        )

        console.print(table)

    @app.command("tools")
    def tools(
        session: str,
    ) -> None:
        """
        Show tool calls for a session.
        """
        conn = connect()
        rows = list_tool_calls(conn, session)

        if not rows:
            console.print("[yellow]No tool calls found for this session.[/yellow]")
            return

        table = Table(title="Tool calls")

        table.add_column("#")
        table.add_column("Tool")
        table.add_column("Arguments")
        table.add_column("Result")
        table.add_column("Created")

        for row in rows:
            try:
                arguments = json.dumps(
                    json.loads(row["arguments"]),
                    ensure_ascii=False,
                    indent=2,
                )
            except json.JSONDecodeError:
                arguments = row["arguments"]

            result = row["result"]

            if len(result) > 500:
                result = result[:500] + "\n..."

            table.add_row(
                str(row["id"]),
                row["tool_name"],
                arguments,
                result,
                row["created_at"],
            )

        console.print(table)
