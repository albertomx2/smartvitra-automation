from pathlib import Path

from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)

ICON_ROOT = Path("assets/presentation/icons/benefits")


class TemplateV2IconRenderer:
    def render(
        self,
        content: TemplateV2PresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        solutions = content.slide03.solutions

        for index, solution in enumerate(
            solutions,
            start=1,
        ):
            icon_path = ICON_ROOT / f"{solution.icon_key}.png"

            if not icon_path.exists():
                raise FileNotFoundError(f"Icon not found: " f"{icon_path}")

            renderer.replace_shape_with_picture(
                ("sv_s03_solution_" f"{index}_icon"),
                icon_path,
            )
