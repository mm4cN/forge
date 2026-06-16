import difflib
import json
from dataclasses import dataclass

from forge.workspace import resolve_in_workspace


@dataclass(frozen=True)
class ApprovalPreview:
    content: str
    lexer: str = "text"
    requires_approval: bool = True


def build_diff(path: str, old_content: str, new_content: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile=f"{path} before",
            tofile=f"{path} after",
            lineterm="",
            n=3,
        )
    )


def build_edit_file_preview(arguments: dict) -> ApprovalPreview:
    path = arguments.get("path")
    new_content = arguments.get("content")

    if not isinstance(path, str) or not isinstance(new_content, str):
        return build_default_preview(arguments)

    file = resolve_in_workspace(path)

    if not file.exists():
        return ApprovalPreview(
            content=f"File:\n{path}\n\nERROR: file does not exist.",
            lexer="text",
        )

    old_content = file.read_text(encoding="utf-8")
    diff = build_diff(path, old_content, new_content)

    if not diff:
        return ApprovalPreview(
            content=f"File:\n{path}\n\nPatch:\n<no changes>",
            lexer="diff",
            requires_approval=False,
        )

    return ApprovalPreview(
        content=f"File:\n{path}\n\nPatch:\n{diff}",
        lexer="diff",
    )


def build_replace_preview(arguments: dict) -> ApprovalPreview:
    path = arguments.get("path")
    old = arguments.get("old")
    new = arguments.get("new")

    if (
        not isinstance(path, str)
        or not isinstance(old, str)
        or not isinstance(new, str)
    ):
        return build_default_preview(arguments)

    file = resolve_in_workspace(path)

    if not file.exists():
        return ApprovalPreview(
            content=f"File:\n{path}\n\nERROR: file does not exist.",
            lexer="text",
        )

    content = file.read_text(encoding="utf-8")

    if old not in content:
        return ApprovalPreview(
            content=f"File:\n{path}\n\nERROR: text to replace was not found.",
            lexer="text",
        )

    updated = content.replace(old, new, 1)
    diff = build_diff(path, content, updated)

    if not diff:
        return ApprovalPreview(
            content=f"File:\n{path}\n\nPatch:\n<no changes>",
            lexer="diff",
            requires_approval=False,
        )

    return ApprovalPreview(
        content=f"File:\n{path}\n\nPatch:\n{diff}",
        lexer="diff",
    )


def build_write_file_preview(arguments: dict) -> ApprovalPreview:
    path = arguments.get("path")
    content = arguments.get("content")

    if not isinstance(path, str) or not isinstance(content, str):
        return build_default_preview(arguments)

    file = resolve_in_workspace(path)

    if file.exists() and file.is_file():
        old_content = file.read_text(encoding="utf-8")
        diff = build_diff(path, old_content, content)

        if not diff:
            return ApprovalPreview(
                content=f"File:\n{path}\n\nPatch:\n<no changes>",
                lexer="diff",
                requires_approval=False,
            )

        return ApprovalPreview(
            content=f"File:\n{path}\n\nPatch:\n{diff}",
            lexer="diff",
        )

    preview = "\n".join(content.splitlines()[:80])

    if len(content.splitlines()) > 80:
        preview += "\n...<truncated>"

    return ApprovalPreview(
        content=f"File:\n{path}\n\nNew file content:\n{preview}",
        lexer="markdown",
    )


def build_command_preview(arguments: dict) -> ApprovalPreview:
    command = arguments.get("command")

    if not isinstance(command, str):
        return build_default_preview(arguments)

    return ApprovalPreview(
        content=f"Command:\n{command}",
        lexer="bash",
    )


def build_default_preview(arguments: dict) -> ApprovalPreview:
    return ApprovalPreview(
        content="Arguments:\n"
        + json.dumps(
            arguments,
            indent=2,
            ensure_ascii=False,
        ),
        lexer="json",
    )


def build_approval_preview(
    tool_name: str,
    arguments: dict,
) -> ApprovalPreview:
    if tool_name == "edit_file":
        return build_edit_file_preview(arguments)

    if tool_name == "replace_in_file":
        return build_replace_preview(arguments)

    if tool_name == "write_file":
        return build_write_file_preview(arguments)

    if tool_name == "run_command":
        return build_command_preview(arguments)

    return build_default_preview(arguments)
