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

Reads a file from the workspace.

Arguments:

- `path`: string
- `start_line`: integer, optional, defaults to `1`
- `max_lines`: integer, optional, defaults to `200`

### write_file

Creates or overwrites a text file.

Arguments:

- `path`: string
- `content`: string

### run_command

Runs a shell command in the current working directory.

Arguments:

- `command`: string

### list_directory

Lists files and directories in a directory.

Arguments:

- `path`: string, optional, defaults to `"."`
- `max_entries`: integer, optional, defaults to `100`

### find_files

Finds files in the workspace.

Prefer this tool when you need to discover files by name or pattern.

Arguments:

- `pattern`: string, optional
- `path`: string, optional, defaults to `.`
- `max_results`: integer, optional, defaults to `100`

Implementation preference:

- Uses `fd` if available.
- Falls back to `find`.

### search_in_files

Searches for text in files.

Arguments:

- `query`
- `path`
- `max_results`

Example:

<tool>
{
  "name": "search_in_files",
  "arguments": {
    "query": "read_file"
  }
}
</tool>

### git_status

Shows current git status.

Arguments:

None.

### git_diff

Shows current git diff.

Arguments:

None.

### replace_in_file

Replaces text in an existing file.

Arguments:

- `path`: string
- `old`: string
- `new`: string

Use this tool when modifying existing files.

Prefer this tool over rewriting entire files.

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
