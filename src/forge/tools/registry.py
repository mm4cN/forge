from forge.tools.list_directory import list_directory
from forge.tools.read_file import read_file
from forge.tools.run_command import run_command
from forge.tools.write_file import write_file


TOOLS = {
    "list_directory": list_directory,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}


def execute_tool(name: str, arguments: dict) -> str:
    if name not in TOOLS:
        return f"ERROR: Unknown tool: {name}"

    try:
        return TOOLS[name](**arguments)
    except TypeError as exc:
        return f"ERROR: Invalid arguments for tool `{name}`: {exc}"
    except Exception as exc:
        return f"ERROR: Tool `{name}` failed: {type(exc).__name__}: {exc}"
