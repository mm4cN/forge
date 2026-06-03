from forge.workspace import resolve_in_workspace


def replace_in_file(
    path: str,
    old: str,
    new: str,
) -> str:
    file = resolve_in_workspace(path)

    if not file.exists():
        return f"ERROR: File does not exist: {path}"

    if not file.is_file():
        return f"ERROR: Path is not a file: {path}"

    content = file.read_text(
        encoding="utf-8",
    )

    occurrences = content.count(old)

    if occurrences == 0:
        return (
            f"ERROR: Pattern not found in {path}"
        )

    if occurrences > 1:
        return (
            f"ERROR: Pattern appears "
            f"{occurrences} times"
        )

    updated = content.replace(
        old,
        new,
    )

    file.write_text(
        updated,
        encoding="utf-8",
    )

    return (
        f"Replaced {occurrences} occurrence(s) "
        f"in {path}"
    )
