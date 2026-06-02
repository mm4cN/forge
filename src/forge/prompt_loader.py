from importlib.resources import files


def load_prompt(name: str) -> str:
    return (
        files("forge.prompts")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )


def build_system_prompt() -> str:
    return "\n\n".join(
        [
            load_prompt("system.md"),
            load_prompt("tools.md"),
            load_prompt("coding.md"),
            load_prompt("workflow.md"),
            load_prompt("path_handling.md"),
        ]
    )
