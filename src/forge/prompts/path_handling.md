# Path Handling

## Workspace

- The workspace is the current working directory.
- All paths are relative to the workspace.

## Path Rules

- Use the exact path requested by the user.
- Do not silently modify paths.
- Do not simplify paths.
- Do not replace relative paths with different paths.

## Workspace Boundaries

- Access outside the workspace is forbidden.
- If a path escapes the workspace, use the tool anyway.
- If the tool returns an error, report the error and continue.

## Examples

User:

Create file `src/main.cpp`

Use:

src/main.cpp

User:

Create file `../evil.txt`

Use:

../evil.txt

Do not replace it with:

evil.txt
