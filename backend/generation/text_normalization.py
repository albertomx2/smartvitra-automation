from __future__ import annotations

import re

_CALLE_ABBREVIATION = re.compile(
    r"(?<!\w)c\s*/\s*",
    flags=re.IGNORECASE,
)

_CALLE_NAME = re.compile(
    r"(?<!\w)calle\s+",
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


def abbreviate_street_for_geocoding(
    value: str,
) -> str:
    """Use the PrefWeb street form known to geocode reliably."""

    return _CALLE_NAME.sub(
        "C/ ",
        value,
    )
