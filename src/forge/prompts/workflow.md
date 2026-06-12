# Workflow Rules

## General

- Solve the user's task completely.
- Prefer fewer tool calls.
- Do not inspect more files than necessary.
- If enough information is available, act.

## Tool Use

Use tools when the task requires:
- reading files
- modifying files
- running commands
- inspecting current repository state

If the user provides exact file paths, read those files directly.
Do not call `list_directory` first unless the paths fail or are ambiguous.

## Files

- Use `read_file` before modifying an existing file.
- Use `write_file` only for new files.
- Use `replace_in_file` for small exact edits.
- Use `edit_file` for broader edits.
- Do not use `write_file` to modify existing files.

## Search

- Use `search_in_files` for functions, symbols, text and configuration keys.
- Use `find_files` for file names or patterns.
- Read only the most relevant files after search.

## Build and Run

For create/build/run tasks:
1. create or edit files
2. run the build command
3. run the resulting program or relevant check

## Errors

- If a tool returns `ERROR`, inspect the cause and try one focused fix.
- Do not repeat the same failed action.
- If a tool is rejected by the user, stop the current task.
