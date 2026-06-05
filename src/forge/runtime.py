import json
import re

from forge.approval import ask_for_approval, requires_approval
from forge.config import load_config
from forge.db import add_model_call, add_tool_call
from forge.providers.factory import get_provider
from forge.prompt_loader import build_system_prompt
from forge.tools.registry import execute_tool


TOOL_RE = re.compile(
    r"<tool>\s*(\{.*?\})\s*</tool>",
    re.DOTALL,
)


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
    max_steps: int = 8,
) -> str:
    provider = get_provider()
    system_prompt = build_system_prompt(model)

    runtime_messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        *messages,
    ]

    for _ in range(max_steps):
        model_response = provider.chat(
            model,
            runtime_messages,
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
            return answer

        name = tool_call["name"]
        arguments = tool_call.get("arguments", {})

        config = load_config()
        approval_mode = bool(config.get("approval_mode", True))

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

                continue

        if name == "__invalid_tool_call__":
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
