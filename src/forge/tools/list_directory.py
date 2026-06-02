from forge.workspace import resolve_in_workspace

def list_directory(
    path: str = ".",
    max_entries: int = 100,
) -> str:
    directory = resolve_in_workspace(path)

    if not directory.exists():
        return f"ERROR: Directory does not exist: {path}"

    if not directory.is_dir():
        return f"ERROR: Path is not a directory: {path}"

    entries = sorted(
        directory.iterdir(),
        key=lambda p: (not p.is_dir(), p.name.lower()),
    )

    total_entries = len(entries)
    entries = entries[:max_entries]

    if not entries:
        return f"Directory is empty: {path}"

    lines: list[str] = []

    for entry in entries:
        suffix = "/" if entry.is_dir() else ""
        lines.append(f"{entry.name}{suffix}")

    if total_entries > max_entries:
        lines.append(f"... truncated, showing {max_entries} of {total_entries} entries")

    return "\n".join(lines)
