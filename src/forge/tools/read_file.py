from forge.workspace import resolve_in_workspace


def read_file(path: str) -> str:
    file = resolve_in_workspace(path)

    if not file.exists():
        return f"ERROR: File does not exist: {path}"

    if not file.is_file():
        return f"ERROR: Path is not a file: {path}"

    return file.read_text(encoding="utf-8")
