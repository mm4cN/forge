import typer

from rich.console import Console

from forge.tools.find_files import find_files
from forge.tools.git_diff import git_diff
from forge.tools.git_status import git_status
from forge.tools.list_directory import list_directory
from forge.tools.read_file import read_file
from forge.tools.replace_in_file import replace_in_file
from forge.tools.search_in_files import search_in_files

console = Console()


def register_tool_commands(app: typer.Typer) -> None:
    @app.command()
    def workspace() -> None:
        """
        Show current workspace.
        """
        from forge.workspace import get_workspace

        console.print(get_workspace())

    @app.command("ls")
    def ls(
        path: str = ".",
    ) -> None:
        """
        List directory contents.
        """
        console.print(list_directory(path=path))

    @app.command()
    def find(
        pattern: str,
        path: str = ".",
    ) -> None:
        """
        Find files.
        """
        console.print(find_files(pattern=pattern, path=path))

    @app.command()
    def search(
        query: str,
        path: str = ".",
    ) -> None:
        """
        Search text in files.
        """
        console.print(search_in_files(query=query, path=path))

    @app.command()
    def cat(
        path: str,
        start_line: int = 1,
        max_lines: int = 200,
    ) -> None:
        """
        Read file.
        """
        console.print(
            read_file(
                path=path,
                start_line=start_line,
                max_lines=max_lines,
            )
        )

    @app.command()
    def status() -> None:
        """
        Show git status.
        """
        console.print(git_status())

    @app.command()
    def diff() -> None:
        """
        Show git diff.
        """
        console.print(git_diff())

    @app.command()
    def replace(
        path: str,
        old: str,
        new: str,
    ) -> None:
        """
        Replace text in file.
        """
        console.print(
            replace_in_file(
                path=path,
                old=old,
                new=new,
            )
        )
