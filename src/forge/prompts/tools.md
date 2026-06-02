# Tool Calling

When you need to use a tool, respond with exactly one `<tool>` block.

The response must contain no Markdown, no explanation, and no fenced code block.

Correct:

<tool>
{
  "name": "write_file",
  "arguments": {
    "path": "hello.cpp",
    "content": "..."
  }
}
</tool>

Incorrect:

I will create the file now.

<tool>
{
  "name": "write_file",
  "arguments": {
    "path": "hello.cpp",
    "content": "..."
  }
}
</tool>

## Available Tools

### read_file

Reads a text file.

Arguments:

- `path`: string

### write_file

Creates or overwrites a text file.

Arguments:

- `path`: string
- `content`: string

### run_command

Runs a shell command in the current working directory.

Arguments:

- `command`: string

## JSON Rules

- Tool calls must contain valid JSON.
- Use double quotes for all keys and string values.
- Do not use single quotes.
- Do not use comments.
- Do not use trailing commas.
- Do not use Markdown inside `<tool>`.
- The `<tool>` block must contain only one JSON object.

## Strict Tool Format

- Tool calls must be wrapped in `<tool>` and `</tool>`.
- Do not use ```json fences for tool calls.
- Do not output a raw JSON object as the final answer when a tool is needed.
- If you decide to use a tool, your entire response must be exactly one `<tool>` block.
