import subprocess

from forge.workspace import get_workspace


def git_diff() -> str:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--no-ext-diff",
        ],
        cwd=get_workspace(),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return f"""ERROR: git_diff failed

STDERR:
{result.stderr}
"""

    if not result.stdout.strip():
        return "No changes."

    return result.stdout
