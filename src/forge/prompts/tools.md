# Tool Calling

When you need to use a tool, respond only with:

<tool>
{
  "name": "tool_name",
  "arguments": {}
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
