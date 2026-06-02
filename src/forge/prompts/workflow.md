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
