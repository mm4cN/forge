import json
import re

from forge.ollama import chat
from forge.prompt_loader import build_system_prompt
from forge.tools.registry import execute_tool


TOOL_RE = re.compile(r"<tool>\s*(\{.*?\})\s*</tool>", re.DOTALL)


def parse_tool_call(text: str) -> dict | None:
    match = TOOL_RE.search(text)
    if not match:
        return None

    return json.loads(match.group(1))


def run_agent(model: str, messages: list[dict[str, str]], max_steps: int = 8) -> str:
    system_prompt = build_system_prompt()

    runtime_messages = [
        {"role": "system", "content": system_prompt},
        *messages,
    ]

    for _ in range(max_steps):
        answer = chat(model, runtime_messages)

        tool_call = parse_tool_call(answer)

        if tool_call is None:
            return answer

        name = tool_call["name"]
        arguments = tool_call.get("arguments", {})

        result = execute_tool(name, arguments)

        runtime_messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        runtime_messages.append(
            {
                "role": "user",
                "content": f"Tool result for `{name}`:\n\n{result}",
            }
        )

    return "ERROR: Reached max agent steps."
