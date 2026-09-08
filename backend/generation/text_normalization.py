from __future__ import annotations

import re

_CALLE_ABBREVIATION = re.compile(
    r"(?<!\w)c\s*/\s*",
    flags=re.IGNORECASE,
)


def expand_street_abbreviations(
    value: str,
) -> str:
    """Expand street abbreviations for display and natural speech."""

    return _CALLE_ABBREVIATION.sub(
        "Calle ",
        value,
    )
