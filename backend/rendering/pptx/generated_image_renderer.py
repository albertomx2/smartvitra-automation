from backend.presentation.generated_images import (
    GeneratedImageProvider,
)
from backend.presentation.models import (
    PresentationSpec,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)


class GeneratedImageRenderer:
    def __init__(
        self,
        provider: GeneratedImageProvider,
    ) -> None:
        self._provider = provider

    def render(
        self,
        spec: PresentationSpec,
        renderer: PowerPointRenderer,
    ) -> None:
        image_path = self._provider.get_before_after_image(spec)

        renderer.replace_picture(
            "sv_s08_after_photo",
            image_path,
        )
