from forge.workspace import resolve_in_workspace


def write_file(path: str, content: str) -> str:
    file = resolve_in_workspace(path)

    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")

    return f"Wrote file: {path}"
