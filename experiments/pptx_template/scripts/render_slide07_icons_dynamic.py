from pathlib import Path

from backend.presentation.content.models import (
    BenefitIconContent,
    GeneratedPresentationContent,
)
from backend.rendering.pptx.benefit_icon_renderer import (
    BenefitIconRenderer,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)

TEMPLATE = Path("experiments/pptx_template/input/template.pptx")

OUTPUT = Path("experiments/pptx_template/output/" "slide07_icons_dynamic.pptx")


content = GeneratedPresentationContent(
    benefit_icons=[
        BenefitIconContent(
            benefit_index=1,
            category="security",
            icon_key="security",
        ),
        BenefitIconContent(
            benefit_index=2,
            category="daylight",
            icon_key="daylight",
        ),
        BenefitIconContent(
            benefit_index=3,
            category="humidity",
            icon_key="humidity",
        ),
        BenefitIconContent(
            benefit_index=4,
            category="maintenance",
            icon_key="maintenance",
        ),
    ]
)


renderer = PowerPointRenderer(TEMPLATE)

BenefitIconRenderer().render(
    content,
    renderer,
)

renderer.save(OUTPUT)

print(f"Written: {OUTPUT}")
