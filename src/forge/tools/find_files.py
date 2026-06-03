import shutil
import subprocess

from forge.workspace import get_workspace, resolve_in_workspace


def find_files(
    pattern: str = "",
    path: str = ".",
    max_results: int = 100,
) -> str:
    directory = resolve_in_workspace(path)
    workspace = get_workspace()

    if not directory.exists():
        return f"ERROR: Directory does not exist: {path}"

    if not directory.is_dir():
        return f"ERROR: Path is not a directory: {path}"

    if shutil.which("fd"):
        glob = pattern or "*"

        if "*" not in glob:
            glob = f"*{glob}*"

        command = [
            "fd",
            "--hidden",
            "--glob",
            "--exclude",
            ".git",
            "--exclude",
            ".venv",
            "--max-results",
            str(max_results),
            glob,
            str(directory),
        ]
    else:
        name_pattern = pattern or "*"

        if "*" not in name_pattern:
            name_pattern = f"*{name_pattern}*"

        command = [
            "find",
            str(directory),
            "-path",
            "*/.git",
            "-prune",
            "-o",
            "-path",
            "*/.venv",
            "-prune",
            "-o",
            "-type",
            "f",
            "-name",
            name_pattern,
            "-print",
        ]

    result = subprocess.run(
        command,
        cwd=workspace,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return f"""ERROR: find_files failed

Command:
{" ".join(command)}

STDERR:
{result.stderr}
"""

    lines = result.stdout.splitlines()
    lines = lines[:max_results]

    if not lines:
        return "No files found."

    return "\n".join(lines)
