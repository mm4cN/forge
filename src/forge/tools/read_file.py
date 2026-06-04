from forge.workspace import resolve_in_workspace


def read_file(
    path: str,
    start_line: int = 1,
    max_lines: int = 200,
) -> str:
    file = resolve_in_workspace(path)

    if not file.exists():
        return f"ERROR: File does not exist: {path}"

    if not file.is_file():
        return f"ERROR: Path is not a file: {path}"

    if start_line < 1:
        return "ERROR: start_line must be >= 1"

    if max_lines < 1:
        return "ERROR: max_lines must be >= 1"

    content = file.read_text(
        encoding="utf-8",
    )

    lines = content.splitlines()

    start_idx = start_line - 1
    end_idx = start_idx + max_lines

    selected_lines = lines[start_idx:end_idx]

    if not selected_lines:
        return "No lines in requested range."

    result: list[str] = []

    for idx, line in enumerate(
        selected_lines,
        start=start_line,
    ):
        result.append(f"{idx:>6}: {line}")

    return "\n".join(result)
