from backend.presentation.content.constraints import (
    TEXT_MAX_CHARACTERS,
)
from backend.presentation.content.models import (
    GeneratedPresentationContent,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)


class Slide08Renderer:
    def render(
        self,
        content: GeneratedPresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        slide08 = content.slide08

        if slide08 is None:
            return

        fields = (
            (
                "sv_s08_before_text",
                slide08.before_text,
            ),
            (
                "sv_s08_after_text",
                slide08.after_text,
            ),
        )

        for shape_name, value in fields:
            result = renderer.set_text_preserving_style(
                shape_name,
                value,
                max_characters=(TEXT_MAX_CHARACTERS[shape_name]),
            )

            if result.estimated_too_long:
                raise ValueError(
                    "Slide 8 text exceeds " "configured limit: " f"{shape_name}"
                )
