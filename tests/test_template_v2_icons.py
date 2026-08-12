from pathlib import Path

from backend.presentation.content.template_v2_fake import (
    FakeTemplateV2ContentGenerator,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_icon_renderer import (
    TemplateV2IconRenderer,
)

TEMPLATE = Path("experiments/pptx_template/input/template.pptx")


def test_template_v2_icons_render():
    renderer = PowerPointRenderer(TEMPLATE)

    content = FakeTemplateV2ContentGenerator().generate()

    TemplateV2IconRenderer().render(
        content,
        renderer,
    )

    for index in range(
        1,
        len(content.slide03.solutions) + 1,
    ):
        shape = renderer.find_shape(f"sv_s03_solution_{index}_icon")

        assert shape is not None
