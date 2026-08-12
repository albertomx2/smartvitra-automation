from backend.presentation.enums import (
    SlideType,
)
from backend.presentation.formatting.money import (
    format_eur,
)
from backend.presentation.models import (
    PresentationSpec,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)


class Slide10Renderer:
    def render(
        self,
        spec: PresentationSpec,
        renderer: PowerPointRenderer,
    ) -> None:
        slide = spec.get_slide(SlideType.INVESTMENT)

        usual_cost = slide.facts.get("usual_cost")

        if usual_cost is None:
            return

        formatted_price = format_eur(usual_cost)

        renderer.set_text_preserving_style(
            "sv_s10_usual_price",
            f"{formatted_price} + IVA",
        )
