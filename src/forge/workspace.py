from pathlib import Path


def get_workspace() -> Path:
    return Path.cwd().resolve()


def resolve_in_workspace(path: str) -> Path:
    workspace = get_workspace()
    resolved = (workspace / path).resolve()

    if not resolved.is_relative_to(workspace):
        raise ValueError(f"Path escapes workspace: {path}")

    return resolved
