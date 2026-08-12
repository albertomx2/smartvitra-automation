from backend.presentation.content.benefit_icons import (
    resolve_benefit_icon,
)
from backend.presentation.content.models import (
    GeneratedPresentationContent,
)
from backend.rendering.pptx.benefit_icon_bindings import (
    BENEFIT_ICON_SHAPE_BINDINGS,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)


class BenefitIconRenderer:
    def render(
        self,
        content: GeneratedPresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        for benefit_icon in content.benefit_icons:
            shape_name = BENEFIT_ICON_SHAPE_BINDINGS[benefit_icon.benefit_index]

            icon_path = resolve_benefit_icon(benefit_icon.icon_key)

            renderer.replace_picture_by_recreation(
                shape_name,
                icon_path,
            )
