# Project Analysis

If the user asks:

- what does this project do
- explain this repository
- analyze the project
- review the codebase

then:

1. list_directory(".")
2. inspect build files
3. inspect README
4. inspect source directory
5. summarize findings

Do not stop after the first tool call.

## Source Verification

When analyzing a project, do not rely only on README files.

After reading README or metadata files, verify the implementation by inspecting source files.

For Python projects:

1. Read `pyproject.toml`.
2. Inspect `src/`.
3. Find CLI entry points.
4. Read the main CLI module.
5. Read the runtime module if present.
6. Then summarize what the project actually does.

Mention if README and implementation appear consistent.
