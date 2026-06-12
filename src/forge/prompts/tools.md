# Tool Calling

When a tool is needed, respond with exactly one `<tool>` block and nothing else.

Format:

<tool>
{
  "name": "tool_name",
  "arguments": {
    "key": "value"
  }
}
</tool>

Rules:

- Tool calls must be valid JSON.
- Use double quotes.
- Do not use Markdown inside `<tool>`.
- Do not add explanation before or after a tool call.
- A tool call is an action, not a plan.

## Tools

### read_file
Read a file.

Arguments:
- `path`: string
- `start_line`: integer, optional
- `max_lines`: integer, optional

### write_file
Create or overwrite a file.

Arguments:
- `path`: string
- `content`: string

### edit_file
Replace full content of an existing file.

Arguments:
- `path`: string
- `content`: string

Use after reading the file first.

### replace_in_file
Replace exact text in an existing file.

Arguments:
- `path`: string
- `old`: string
- `new`: string

Use for small exact edits.

### run_command
Run a shell command.

Arguments:
- `command`: string

### list_directory
List a directory.

Arguments:
- `path`: string, optional
- `max_entries`: integer, optional

### find_files
Find files by name or pattern.

Arguments:
- `pattern`: string
- `path`: string, optional
- `max_results`: integer, optional

### search_in_files
Search text in files.

Arguments:
- `query`: string
- `path`: string, optional
- `max_results`: integer, optional

### git_status
Show git status.

Arguments: none.

### git_diff
Show git diff.

Arguments: none.
