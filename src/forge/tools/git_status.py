import subprocess

from forge.workspace import get_workspace


def git_status() -> str:
    result = subprocess.run(
        [
            "git",
            "status",
            "--short",
        ],
        cwd=get_workspace(),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return f"""ERROR: git_status failed

STDERR:
{result.stderr}
"""

    if not result.stdout.strip():
        return "Working tree clean."

    return result.stdout
