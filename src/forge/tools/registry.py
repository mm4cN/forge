from forge.tools.find_files import find_files
from forge.tools.list_directory import list_directory
from forge.tools.read_file import read_file
from forge.tools.run_command import run_command
from forge.tools.search_in_files import search_in_files
from forge.tools.write_file import write_file
from forge.tools.git_diff import git_diff
from forge.tools.git_status import git_status
from forge.tools.replace_in_file import replace_in_file
from forge.tools.edit_file import edit_file

TOOLS = {
    "find_files": find_files,
    "list_directory": list_directory,
    "read_file": read_file,
    "run_command": run_command,
    "search_in_files": search_in_files,
    "write_file": write_file,
    "git_status": git_status,
    "git_diff": git_diff,
    "replace_in_file": replace_in_file,
    "edit_file": edit_file,
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
