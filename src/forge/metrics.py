def tokens_per_second(
    total_tokens: int | None,
    duration_ms: int | None,
) -> float | None:

    if total_tokens is None:
        return None

    if duration_ms is None:
        return None

    if duration_ms <= 0:
        return None

    return total_tokens / (duration_ms / 1000)
