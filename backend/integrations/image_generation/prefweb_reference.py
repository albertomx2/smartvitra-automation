from __future__ import annotations

import re
from pathlib import Path

import cairosvg  # type: ignore[import-untyped]


def _sanitize_prefweb_svg(
    svg: str,
) -> str:
    """
    PrefWeb SVGs may contain gradient/pattern paint references
    that CairoSVG does not parse reliably.

    For the AI reference image we care about geometry and
    composition, not decorative gradients, so unsupported
    paint-server references are converted to safe flat colors.
    """

    # fill="url(#gradient)"
    svg = re.sub(
        r'fill\s*=\s*["\']url\([^"\']+\)["\']',
        'fill="#FFFFFF"',
        svg,
        flags=re.IGNORECASE,
    )

    # stroke="url(#gradient)"
    svg = re.sub(
        r'stroke\s*=\s*["\']url\([^"\']+\)["\']',
        'stroke="#000000"',
        svg,
        flags=re.IGNORECASE,
    )

    # style="... fill:url(...); ..."
    svg = re.sub(
        r"fill\s*:\s*url\([^)]+\)",
        "fill:#FFFFFF",
        svg,
        flags=re.IGNORECASE,
    )

    # style="... stroke:url(...); ..."
    svg = re.sub(
        r"stroke\s*:\s*url\([^)]+\)",
        "stroke:#000000",
        svg,
        flags=re.IGNORECASE,
    )

    return svg


def render_prefweb_svg_reference(
    *,
    svg: str,
    output_path: Path,
) -> Path:
    if not svg.strip():
        raise ValueError("PrefWeb SVG is empty")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sanitized_svg = _sanitize_prefweb_svg(
        svg,
    )

    cairosvg.svg2png(
        bytestring=sanitized_svg.encode(
            "utf-8",
        ),
        write_to=str(output_path),
        output_width=1200,
    )

    if not output_path.exists():
        raise RuntimeError("Could not render PrefWeb SVG")

    if output_path.stat().st_size == 0:
        raise RuntimeError("Rendered PrefWeb reference is empty")

    return output_path
