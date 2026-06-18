from dataclasses import dataclass
import json
import re
from rich.console import Console

from forge.approval import ask_for_approval, requires_approval
from forge.config import load_config
from forge.db import add_model_call, add_tool_call
from forge.providers.base import ModelInfo, ModelResponse
from forge.providers.factory import get_provider
from forge.prompt_loader import build_system_prompt
from forge.tools.registry import execute_tool
from forge.project_memory import build_project_memory_prompt, sync_project_memory

TOOL_RE = re.compile(
    r"<tool>\s*(\{.*?\})\s*</tool>",
    re.DOTALL,
)

console = Console()


@dataclass(slots=True)
class AgentResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    duration_ms: int = 0
    steps: int = 0


def compact_tool_result(
    result: str,
    max_tool_result_chars: int,
) -> str:
    if len(result) <= max_tool_result_chars:
        return result

    return result[:max_tool_result_chars] + "\n\n...<truncated>"


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


def print_token_info(model_response: ModelResponse, info: ModelInfo) -> None:
    prompt_tokens = model_response.prompt_tokens

    usage_pct = None
    if prompt_tokens is not None and info.context_window > 0:
        usage_pct = (prompt_tokens / info.context_window) * 100

    usage = "-"
    if usage_pct is not None:
        usage = f"{usage_pct:.1f}%"

    console.print(
        "[dim]"
        f"tokens: input={prompt_tokens or '-'} / {info.context_window} ({usage}), "
        f"output={model_response.completion_tokens or '-'}, "
        f"total={model_response.total_tokens or '-'}, "
        f"duration={model_response.duration_ms or '-'} ms"
        "[/dim]"
    )


def run_agent(
    model: str,
    messages: list[dict[str, str]],
    session_id: str | None = None,
    conn=None,
    max_steps: int = 12,
    show_steps: bool = False,
) -> AgentResult:
    provider = get_provider()
    info = provider.get_model_info(model)
    if show_steps:
        console.print(f"[dim]model: {model} | context window: {info.context_window}[/dim]")

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
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_tokens = 0
    total_duration_ms = 0

    for step in range(1, max_steps + 1):
        if show_steps:
            context_chars = sum(len(message["content"]) for message in runtime_messages)
            console.print(
                f"[dim]step: {step}/{max_steps} | "
                f"context: {context_chars} chars | "
                f"messages: {len(runtime_messages)}[/dim]"
            )

        model_response = provider.chat(
            model,
            runtime_messages,
        )
        if show_steps:
            print_token_info(model_response, info)

        total_prompt_tokens += model_response.prompt_tokens or 0
        total_completion_tokens += model_response.completion_tokens or 0
        total_tokens += model_response.total_tokens or 0
        total_duration_ms += model_response.duration_ms or 0

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
                console.print(f"[dim]Final answer[/dim]")

            return AgentResult(
                text=answer,
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                total_tokens=total_tokens,
                duration_ms=total_duration_ms,
                steps=step,
            )

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
                return AgentResult(
                    text=f"Tool `{name}` was rejected by the user. No changes were made.",
                    prompt_tokens=total_prompt_tokens,
                    completion_tokens=total_completion_tokens,
                    total_tokens=total_tokens,
                    duration_ms=total_duration_ms,
                    steps=step,
                )

        if name == "__invalid_tool_call__":
            invalid_tool_calls += 1
            if invalid_tool_calls >= 2:
                return AgentResult(
                    text=(
                        "ERROR: Model repeatedly produced invalid tool calls. "
                        "Try a simpler prompt, increase --max-steps, or use a stronger model."
                    ),
                    prompt_tokens=total_prompt_tokens,
                    completion_tokens=total_completion_tokens,
                    total_tokens=total_tokens,
                    duration_ms=total_duration_ms,
                    steps=step,
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
        if show_steps:
            console.print(f"[dim]tool result: {len(result)} chars[/dim]")

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

        compact_result = compact_tool_result(result, info.max_tool_results_chars)
        runtime_messages.append(
            {
                "role": "user",
                "content": (f"Tool result for `{name}`:\n\n{compact_result}"),
            }
        )

    return AgentResult(
        text="ERROR: Reached maximum agent steps.",
        prompt_tokens=total_prompt_tokens,
        completion_tokens=total_completion_tokens,
        total_tokens=total_tokens,
        duration_ms=total_duration_ms,
        steps=max_steps,
    )
