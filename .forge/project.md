# Forge Project Memory

## Overview

Forge is a lightweight local-first coding assistant / agent runtime.

It provides:

- CLI commands for ask, agent, chat, review, model management and tracking
- provider abstraction for local and hosted LLMs
- workspace-aware tools
- persistent SQLite-backed sessions
- approval mode for potentially destructive actions
- model usage and tool-call tracking

Forge is not intended to become a large AI framework.
Keep the codebase small, explicit and easy to understand.

## Architecture

Main modules:

- `src/forge/cli.py`
  - CLI entrypoint
  - should stay thin
  - registers command modules only

- `src/forge/commands/`
  - Typer command modules
  - each file owns one command area

- `src/forge/runtime.py`
  - agent loop
  - model calls
  - tool parsing and execution

- `src/forge/tools/`
  - workspace-aware tool implementations

- `src/forge/providers/`
  - model provider abstraction and implementations

- `src/forge/db.py`
  - SQLite schema and persistence helpers

- `src/forge/project_memory.py`
  - project memory discovery, hashing and sync

- `src/forge/prompts/`
  - prompt fragments used to steer the agent

## Design Rules

- Keep `cli.py` thin.
- Prefer small, focused modules.
- Prefer explicit functions over clever abstractions.
- Use type hints.
- Use `pathlib` for filesystem paths.
- Use `sqlite3` directly; do not introduce an ORM.
- Use Ruff formatting.
- Prefer workspace-relative paths in tool calls and examples.
- Avoid framework creep.
- Do not introduce LangChain-style abstractions.
- Do not add embeddings or vector databases unless there is a proven need.
- Keep provider-specific logic inside provider modules.
- Keep tool implementations deterministic and side-effect-aware.

## Safety Rules

Potentially destructive tools must require approval:

- `write_file`
- `edit_file`
- `replace_in_file`
- `run_command`

The agent should prefer:

- `read_file` before editing an existing file
- `edit_file` for broader file modifications
- `replace_in_file` for small exact replacements
- `run_command` only when verification is useful

Do not silently modify files.

## Current Capabilities

Forge currently supports:

- Ollama provider
- Gemini provider
- ask mode
- agent mode
- interactive chat
- review command
- approval mode
- model usage tracking
- tool-call tracking
- throughput metrics
- project memory tracking

## Development Workflow

Before committing changes, prefer running:

```bash
ruff format .
ruff check .

