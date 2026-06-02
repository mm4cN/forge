import subprocess

from forge.workspace import get_workspace


def run_command(command: str) -> str:
    result = subprocess.run(
        command,
        shell=True,
        cwd=get_workspace(),
        capture_output=True,
        text=True,
    )

    return f"""Workspace: {get_workspace()}
Command: {command}
Exit code: {result.returncode}

STDOUT:
{result.stdout}

STDERR:
{result.stderr}
"""
