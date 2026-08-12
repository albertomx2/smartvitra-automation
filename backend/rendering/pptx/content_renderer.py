from backend.presentation.content.constraints import (
    TEXT_MAX_CHARACTERS,
)
from backend.presentation.content.models import (
    GeneratedPresentationContent,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.semantic_bindings import (
    SEMANTIC_CARD_BINDINGS,
)


class PresentationContentRenderer:
    def render(
        self,
        content: GeneratedPresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        for text_item in content.texts:
            result = renderer.set_text_preserving_style(
                text_item.shape_name,
                text_item.text,
                max_characters=(TEXT_MAX_CHARACTERS[text_item.shape_name]),
            )

            if result.estimated_too_long:
                raise ValueError(
                    "Generated text exceeds "
                    "configured limit: "
                    f"{text_item.shape_name}"
                )

        if content.slide06 is not None:
            renderer.set_text_preserving_style(
                "sv_s06_subtitle",
                content.slide06.subtitle,
                max_characters=(TEXT_MAX_CHARACTERS["sv_s06_subtitle"]),
            )

            for index in range(1, 9):
                shape_name = f"sv_s06_solution_{index}"

                line_index = index - 1

                if line_index < len(content.slide06.solutions.lines):
                    value = content.slide06.solutions.lines[line_index]
                else:
                    value = ""

                renderer.set_text_preserving_style(
                    shape_name,
                    value,
                    max_characters=(TEXT_MAX_CHARACTERS[shape_name]),
                )

        for color_item in content.semantic_colors:
            binding = SEMANTIC_CARD_BINDINGS[color_item.slot]

            renderer.set_shape_border_color(
                binding.outer_shape,
                color_item.semantic_color,
            )

            renderer.set_shape_fill_color(
                binding.accent_shape,
                color_item.semantic_color,
            )
