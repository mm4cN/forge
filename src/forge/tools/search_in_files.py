import shutil
import subprocess

from forge.workspace import get_workspace, resolve_in_workspace


def search_in_files(
    query: str,
    path: str = ".",
    max_results: int = 100,
) -> str:
    directory = resolve_in_workspace(path)

    if not directory.exists():
        return f"ERROR: Directory does not exist: {path}"

    if not directory.is_dir():
        return f"ERROR: Path is not a directory: {path}"

    workspace = get_workspace()

    if shutil.which("rg"):
        command = [
            "rg",
            "--hidden",
            "--glob",
            "!.git",
            "--glob",
            "!.venv",
            "--line-number",
            "--column",
            "--max-count",
            str(max_results),
            query,
            str(directory),
        ]
    else:
        command = [
            "grep",
            "-RIn",
            "--exclude-dir=.git",
            "--exclude-dir=.venv",
            query,
            str(directory),
        ]

    result = subprocess.run(
        command,
        cwd=workspace,
        capture_output=True,
        text=True,
    )

    if result.returncode == 1:
        return "No matches found."

    if result.returncode != 0:
        return f"""ERROR: search_in_files failed

Command:
{" ".join(command)}

STDERR:
{result.stderr}
"""

    lines = result.stdout.splitlines()
    lines = lines[:max_results]

    if not lines:
        return "No matches found."

    return "\n".join(lines)
