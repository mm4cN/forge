import json
import re

from rich.console import Console

from forge.approval import ask_for_approval, requires_approval
from forge.config import load_config
from forge.db import add_model_call, add_tool_call
from forge.providers.factory import get_provider
from forge.prompt_loader import build_system_prompt
from forge.tools.registry import execute_tool
from forge.project_memory import build_project_memory_prompt, sync_project_memory

TOOL_RE = re.compile(
    r"<tool>\s*(\{.*?\})\s*</tool>",
    re.DOTALL,
)

console = Console()


def parse_tool_call(text: str) -> dict | None:
    match = TOOL_RE.search(text)

    if not match:
        return None

    raw_json = match.group(1)

    try:
        return json.loads(raw_json)

    except json.JSONDecodeError as exc:
        return {
            "name": "__invalid_tool_call__",
            "arguments": {
                "error": str(exc),
                "raw": raw_json,
            },
        }


def run_agent(
    model: str,
    messages: list[dict[str, str]],
    session_id: str | None = None,
    conn=None,
    max_steps: int = 12,
    show_steps: bool = False,
) -> str:
    provider = get_provider()
    system_prompt = build_system_prompt("agent")

    project_memory = None
    if conn is not None:
        project_memory = sync_project_memory(conn)

    runtime_messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
    ]
    if project_memory is not None:
        runtime_messages.append(
            {
                "role": "system",
                "content": build_project_memory_prompt(project_memory),
            }
        )
    runtime_messages.extend(messages)

    invalid_tool_calls = 0

    for step in range(1, max_steps + 1):
        if show_steps:
            console.print(f"[dim][step {step}/{max_steps}] Thinking...[/dim]")
            context_chars = sum(len(message["content"]) for message in runtime_messages)
            console.print(f"[dim]context: {context_chars} chars[/dim]")
            console.print(f"[dim]messages: {len(runtime_messages)}[/dim]")

        model_response = provider.chat(
            model,
            runtime_messages,
        )
        if show_steps:
            console.print(
                "[dim]"
                f"tokens: input={model_response.prompt_tokens or '-'}, "
                f"output={model_response.completion_tokens or '-'}, "
                f"total={model_response.total_tokens or '-'}, "
                f"duration={model_response.duration_ms or '-'} ms"
                "[/dim]"
            )

        answer = model_response.text
        if conn is not None and session_id is not None:
            add_model_call(
                conn=conn,
                session_id=session_id,
                provider=provider.name,
                model=model,
                prompt_tokens=model_response.prompt_tokens,
                completion_tokens=model_response.completion_tokens,
                total_tokens=model_response.total_tokens,
                duration_ms=model_response.duration_ms,
            )
        tool_call = parse_tool_call(answer)

        if tool_call is None:
            if show_steps:
                console.print(f"[dim][{step}/{max_steps}] Final answer[/dim]")
                console.print(
                    "[dim]"
                    f"tokens: input={model_response.prompt_tokens or '-'}, "
                    f"output={model_response.completion_tokens or '-'}, "
                    f"total={model_response.total_tokens or '-'}, "
                    f"duration={model_response.duration_ms or '-'} ms"
                    "[/dim]"
                )

            return answer

        name = tool_call["name"]
        arguments = tool_call.get("arguments", {})

        config = load_config()
        approval_mode = bool(config.get("approval_mode", True))

        if show_steps:
            console.print(f"[cyan][step {step}/{max_steps}] Tool:[/cyan] {name}")

            path = arguments.get("path")
            query = arguments.get("query")
            command = arguments.get("command")
            pattern = arguments.get("pattern")

            if path:
                console.print(f"[dim]path: {path}[/dim]")
            if query:
                console.print(f"[dim]query: {query}[/dim]")
            if pattern:
                console.print(f"[dim]pattern: {pattern}[/dim]")
            if command:
                console.print(f"[dim]command: {command}[/dim]")

        if approval_mode and requires_approval(name):
            approved = ask_for_approval(
                tool_name=name,
                arguments=arguments,
            )

            if not approved:
                result = f"ERROR: Tool `{name}` was rejected by the user."
                runtime_messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )
                runtime_messages.append(
                    {
                        "role": "user",
                        "content": (f"Tool result for `{name}`:\n\n{result}"),
                    }
                )
                return f"Tool `{name}` was rejected by the user. No changes were made."

        if name == "__invalid_tool_call__":
            invalid_tool_calls += 1
            if invalid_tool_calls >= 2:
                return (
                    "ERROR: Model repeatedly produced invalid tool calls. "
                    "Try a simpler prompt, increase --max-steps, or use a stronger model."
                )
            if show_steps:
                console.print(
                    f"[yellow][step {step}/{max_steps}] Invalid tool call[/yellow]"
                )
                console.print(f"[dim]{arguments['error']}[/dim]")

            runtime_messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            runtime_messages.append(
                {
                    "role": "user",
                    "content": (
                        "Your previous tool call was invalid JSON.\n\n"
                        f"JSON parser error:\n{arguments['error']}\n\n"
                        "Retry using valid JSON only.\n"
                        "Use double quotes for all keys and string values.\n"
                        "Do not use comments.\n"
                        "Do not use trailing commas.\n"
                        "Do not use markdown inside <tool> blocks."
                    ),
                }
            )

            continue

        invalid_tool_calls = 0

        result = execute_tool(
            name,
            arguments,
        )
        if conn is not None and session_id is not None:
            add_tool_call(
                conn=conn,
                session_id=session_id,
                tool_name=name,
                arguments=arguments,
                result=result,
            )

        runtime_messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        runtime_messages.append(
            {
                "role": "user",
                "content": (f"Tool result for `{name}`:\n\n{result}"),
            }
        )

    return "ERROR: Reached maximum agent steps."
