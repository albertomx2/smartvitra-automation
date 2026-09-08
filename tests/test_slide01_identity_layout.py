from pathlib import Path

from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches

from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_layout import (
    TemplateV2LayoutRenderer,
)

TEMPLATE = Path(
    "experiments/pptx_template/input/template.pptx",
)


def test_customer_name_uses_available_width_without_wrapping() -> None:
    renderer = PowerPointRenderer(
        TEMPLATE,
    )

    TemplateV2LayoutRenderer().render_slide01_identity(
        renderer=renderer,
    )

    name = renderer.find_shape(
        "sv_s01_customer_name",
    )
    cover_photo = renderer.find_shape(
        "sv_s01_cover_photo",
    )

    assert name.width == Inches(5.45)
    assert name.left + name.width <= cover_photo.left
    assert name.text_frame.word_wrap is False
    assert name.text_frame.auto_size == MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
