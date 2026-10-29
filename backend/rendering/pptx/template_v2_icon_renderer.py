from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)


class TemplateV2IconRenderer:
    def render(
        self,
        content: TemplateV2PresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        """Keep the template-native hyphens used by the redesigned slide 3."""

        del content, renderer
