from pathlib import Path

from backend.presentation.content.icon_catalog import (
    get_benefit_icon_path,
)
from backend.rendering.pptx.bindings import (
    BENEFIT_ICON_BINDINGS,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)

INPUT = Path("experiments/pptx_template/input/template.pptx")

OUTPUT = Path("experiments/pptx_template/output/" "slide07_icons_fake.pptx")


renderer = PowerPointRenderer(INPUT)

icon_keys = (
    "thermal",
    "acoustic",
    "energy",
    "home_value",
)

for index, icon_key in enumerate(
    icon_keys,
    start=1,
):
    renderer.replace_picture(
        BENEFIT_ICON_BINDINGS[index],
        get_benefit_icon_path(icon_key),
    )

renderer.save(OUTPUT)

print(f"Written: {OUTPUT}")
