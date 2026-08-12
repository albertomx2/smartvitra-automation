def fit_text_to_limit(
    text: str,
    max_characters: int,
) -> str:
    cleaned = " ".join(text.split())

    if len(cleaned) <= max_characters:
        return cleaned

    candidate = cleaned[:max_characters].rstrip()

    if " " in candidate:
        candidate = candidate.rsplit(
            " ",
            1,
        )[0]

    candidate = candidate.rstrip(" ,;:-")

    if candidate and candidate[-1] not in ".!?":
        candidate += "."

    return candidate
