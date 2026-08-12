from pathlib import Path

from backend.presentation.content.generator import (
    PresentationContentGenerator,
)
from backend.presentation.generated_images import (
    GeneratedImageProvider,
)
from backend.presentation.models import (
    PresentationSpec,
)
from backend.rendering.pptx.assets import (
    ImageAssetResolver,
)
from backend.rendering.pptx.content_renderer import (
    PresentationContentRenderer,
)
from backend.rendering.pptx.generated_image_renderer import (
    GeneratedImageRenderer,
)
from backend.rendering.pptx.image_renderer import (
    PresentationImageRenderer,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.slide08_renderer import (
    Slide08Renderer,
)
from backend.rendering.pptx.slide10_renderer import (
    Slide10Renderer,
)
from backend.rendering.pptx.slide11_renderer import (
    Slide11Renderer,
)


class PptxPresentationPipeline:
    def __init__(
        self,
        content_generator: PresentationContentGenerator,
        image_asset_resolver: ImageAssetResolver,
        generated_image_provider: GeneratedImageProvider | None = None,
    ) -> None:
        self._content_generator = content_generator

        self._content_renderer = PresentationContentRenderer()

        self._slide08_renderer = Slide08Renderer()

        self._slide10_renderer = Slide10Renderer()

        self._slide11_renderer = Slide11Renderer()

        self._image_renderer = PresentationImageRenderer(image_asset_resolver)

        self._generated_image_renderer = (
            GeneratedImageRenderer(generated_image_provider)
            if generated_image_provider is not None
            else None
        )

    def render(
        self,
        spec: PresentationSpec,
        template_path: Path,
        output_path: Path,
    ) -> Path:
        content = self._content_generator.generate(spec)

        renderer = PowerPointRenderer(template_path)

        self._content_renderer.render(
            content,
            renderer,
        )

        self._slide08_renderer.render(
            content,
            renderer,
        )

        self._slide10_renderer.render(
            spec,
            renderer,
        )

        self._slide11_renderer.render(
            spec,
            renderer,
        )

        self._image_renderer.render(
            spec,
            renderer,
        )

        if self._generated_image_renderer is not None:
            self._generated_image_renderer.render(
                spec,
                renderer,
            )

        renderer.save(output_path)

        return output_path
