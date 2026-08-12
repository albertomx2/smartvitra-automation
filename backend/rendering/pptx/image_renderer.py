from backend.presentation.models import (
    PresentationSpec,
)
from backend.rendering.pptx.assets import (
    ImageAssetResolver,
)
from backend.rendering.pptx.bindings import (
    IMAGE_BINDINGS,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)


class PresentationImageRenderer:
    def __init__(
        self,
        asset_resolver: ImageAssetResolver,
    ) -> None:
        self._asset_resolver = asset_resolver

    def render(
        self,
        spec: PresentationSpec,
        renderer: PowerPointRenderer,
    ) -> None:
        for binding in IMAGE_BINDINGS:
            slide = spec.get_slide(binding.slide_type)

            matching_photos = [
                photo for photo in slide.photos if (photo.role == binding.photo_role)
            ]

            if not matching_photos:
                continue

            photo = matching_photos[0]

            image_path = self._asset_resolver.resolve(photo.storage_key)

            renderer.replace_picture(
                binding.shape_name,
                image_path,
            )
