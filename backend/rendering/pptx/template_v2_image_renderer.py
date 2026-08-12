from pathlib import Path

from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_image_bindings import (
    TEMPLATE_V2_IMAGE_BINDINGS,
)


class TemplateV2ImageRenderer:
    def render(
        self,
        *,
        renderer: PowerPointRenderer,
        images: dict[str, Path],
    ) -> None:
        for key, image_path in images.items():
            binding = TEMPLATE_V2_IMAGE_BINDINGS.get(key)

            if binding is None:
                raise KeyError(f"Unknown template image key: {key}")

            if not image_path.exists():
                raise FileNotFoundError(image_path)

            renderer.replace_shape_with_picture(
                binding.shape_name,
                image_path,
            )
