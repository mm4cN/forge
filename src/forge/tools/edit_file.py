import difflib

from forge.workspace import resolve_in_workspace


def edit_file(
    path: str,
    content: str,
) -> str:
    file = resolve_in_workspace(path)

    if not file.exists():
        return f"ERROR: File does not exist: {path}"

    if not file.is_file():
        return f"ERROR: Path is not a file: {path}"

    old_content = file.read_text(encoding="utf-8")

    if old_content == content:
        return f"No changes in {path}."

    diff = "\n".join(
        difflib.unified_diff(
            old_content.splitlines(),
            content.splitlines(),
            fromfile=f"{path} before",
            tofile=f"{path} after",
            lineterm="",
            n=3,
        )
    )

    file.write_text(content, encoding="utf-8")

    return f"Edited {path}.\n\nPatch:\n```diff\n{diff}\n```"
