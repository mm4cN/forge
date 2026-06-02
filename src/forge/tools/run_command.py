import subprocess


def run_command(command: str) -> str:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )

    return f"""Exit code: {result.returncode}

STDOUT:
{result.stdout}

STDERR:
{result.stderr}
"""
