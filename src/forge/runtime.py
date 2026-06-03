import json
import re

from forge.ollama import chat
from forge.prompt_loader import build_system_prompt
from forge.tools.registry import execute_tool


TOOL_RE = re.compile(
    r"<tool>\s*(\{.*?\})\s*</tool>",
    re.DOTALL,
)
FINAL_TOOLS = {
    "find_files",
    "search_in_files",
    "list_directory",
}

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
    max_steps: int = 8,
) -> str:
    system_prompt = build_system_prompt()

    runtime_messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        *messages,
    ]

    for _ in range(max_steps):
        answer = chat(
            model,
            runtime_messages,
        )

        tool_call = parse_tool_call(answer)

        if tool_call is None:
            return answer

        name = tool_call["name"]
        arguments = tool_call.get("arguments", {})

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
        if name in FINAL_TOOLS:
            return result

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
                    f"Tool result for `{name}`:\n\n"
                    f"{result}"
                ),
            }
        )

    return "ERROR: Reached maximum agent steps."
