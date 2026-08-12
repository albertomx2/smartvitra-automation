from pathlib import Path

from backend.presentation.content.generator import (
    FakePresentationContentGenerator,
)
from backend.presentation.generated_images import (
    LocalGeneratedImageProvider,
)
from backend.rendering.pptx.assets import (
    LocalImageAssetResolver,
)
from backend.rendering.pptx.pipeline import (
    PptxPresentationPipeline,
)
from scripts.inspect_presentation_spec import (
    spec,
)

TEMPLATE = Path("experiments/pptx_template/input/" "template.pptx")

OUTPUT = Path("experiments/pptx_template/output/" "slide08_fake.pptx")

STORAGE = Path("experiments/pptx_template/storage")

AFTER = Path("experiments/pptx_template/input/" "images/after_test.jpg")

pipeline = PptxPresentationPipeline(
    content_generator=(FakePresentationContentGenerator()),
    image_asset_resolver=(LocalImageAssetResolver(STORAGE)),
    generated_image_provider=(LocalGeneratedImageProvider(AFTER)),
)

result = pipeline.render(
    spec=spec,
    template_path=TEMPLATE,
    output_path=OUTPUT,
)

print(result)
