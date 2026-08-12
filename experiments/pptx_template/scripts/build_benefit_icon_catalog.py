from pathlib import Path

import cairosvg

SOURCE = Path("experiments/pptx_template/input/lucide_svg")

OUTPUT = Path("assets/presentation/icons/benefits")

ICON_COLOR = "#46B1E1"


OUTPUT.mkdir(
    parents=True,
    exist_ok=True,
)


for svg_path in sorted(SOURCE.glob("*.svg")):
    output_path = OUTPUT / f"{svg_path.stem}.png"

    svg_text = svg_path.read_text(encoding="utf-8")

    svg_text = svg_text.replace(
        "currentColor",
        ICON_COLOR,
    )

    cairosvg.svg2png(
        bytestring=svg_text.encode("utf-8"),
        write_to=str(output_path),
        output_width=256,
        output_height=256,
    )

    print(f"{svg_path.name:24}" f" -> {output_path.name}" f" [{ICON_COLOR}]")
