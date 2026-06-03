# Workflow Rules

## Files

- If a file does not exist yet, use `write_file` before `read_file`.
- Do not read files you have just been asked to create unless you have created them first.

## Build Tasks

For tasks like "create, compile and run", the expected order is:

1. `write_file`
2. `run_command` to compile
3. `run_command` to execute

## Error Handling

- If a tool returns `ERROR`, fix the issue and continue.
- Never stop after the first tool failure.
- Investigate the error and try again.

## Agent Loop

- Solve the user's task completely.
- Do not stop after creating files.
- Do not stop after compilation.
- Continue until the requested result is achieved.

## Project Inspection

- Before modifying an existing project, inspect the workspace with `list_directory`.
- Use `list_directory` to discover files before reading them.
- Do not guess project structure when a tool can inspect it.

## Mandatory Tool Usage

When the user asks to:

- create a file
- modify a file
- read a file
- compile code
- execute code
- inspect a directory

you MUST use tools.

You are not allowed to claim that an action was completed unless a tool was executed successfully.

Incorrect:

"The file was created successfully."

Correct:

<tool>
{
  "name": "write_file",
  ...
}
</tool>

## Search Workflow

- Use `find_files` when looking for files by name.
- Use `search_in_files` when looking for text, symbols, functions, classes, includes, imports, or configuration keys.
- Prefer search tools before guessing file paths.
- Prefer reading only the most relevant files after search.

## Git Workflow

- Before modifying an existing project, inspect git status.
- Use git diff to understand existing changes.
- Do not assume the workspace is clean.

## File Modification

- Prefer `replace_in_file` when changing existing files.
- Do not rewrite an entire file when a small modification is sufficient.
- Use `read_file` first if you need context.

## Large Files

- Prefer reading files in chunks.
- Use read_file with start_line and max_lines when inspecting large files.
- Avoid reading entire files when only a small section is needed.

## Finding Code

- If the user asks to find a function, class, symbol, or implementation, use `search_in_files`.
- If the user asks to find a file by name, use `find_files`.
- For "find implementation of X", use `search_in_files` with `query` set to `X`.
