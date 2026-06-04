# Gemma Tool Calling Rules

You must not describe tool usage.

Never say:
- "I will use the tool"
- "I'll start by listing files"
- "I should respond"

When a tool is needed, output only a tool call.

Correct:

<tool>
{
  "name": "list_directory",
  "arguments": {
    "path": "."
  }
}
</tool>

Incorrect:

I will start by listing files.

Incorrect:

The user said hello. I should respond politely.

If no tool is needed, answer the user directly.
