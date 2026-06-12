import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path

import sqlite3

from forge.db import get_project_by_workspace, upsert_project
from forge.workspace import get_workspace


@dataclass
class ProjectMemory:
    name: str
    workspace_path: str
    git_remote: str | None
    project_md_path: str
    project_md_sha256: str
    project_md_content: str


def calculate_sha256(
    content: str,
) -> str:
    return hashlib.sha256(
        content.encode("utf-8"),
    ).hexdigest()


def get_git_remote(
    workspace: Path,
) -> str | None:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=workspace,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None

    if result.returncode != 0:
        return None

    remote = result.stdout.strip()

    if not remote:
        return None

    return remote


def get_project_memory_path(
    workspace: Path,
) -> Path:
    return workspace / ".forge" / "project.md"


def discover_project_memory() -> ProjectMemory | None:
    workspace = get_workspace()
    project_md_path = get_project_memory_path(workspace)

    if not project_md_path.exists():
        return None

    if not project_md_path.is_file():
        return None

    content = project_md_path.read_text(encoding="utf-8")
    sha256 = calculate_sha256(content)

    return ProjectMemory(
        name=workspace.name,
        workspace_path=str(workspace),
        git_remote=get_git_remote(workspace),
        project_md_path=str(project_md_path),
        project_md_sha256=sha256,
        project_md_content=content,
    )


def sync_project_memory(
    conn: sqlite3.Connection,
) -> ProjectMemory | None:
    memory = discover_project_memory()

    if memory is None:
        return None

    existing = get_project_by_workspace(
        conn,
        memory.workspace_path,
    )

    if (
        existing is not None
        and existing["project_md_sha256"] == memory.project_md_sha256
    ):
        return memory

    upsert_project(
        conn=conn,
        name=memory.name,
        workspace_path=memory.workspace_path,
        git_remote=memory.git_remote,
        project_md_path=memory.project_md_path,
        project_md_sha256=memory.project_md_sha256,
        project_md_content=memory.project_md_content,
    )

    return memory


def build_project_memory_prompt(
    memory: ProjectMemory,
) -> str:
    return f"""# Project Memory
        The following instructions are specific to the current repository.
        Project: {memory.name}
        Workspace: {memory.workspace_path}
        Git remote: {memory.git_remote or "none"}
        {memory.project_md_content}
    """
