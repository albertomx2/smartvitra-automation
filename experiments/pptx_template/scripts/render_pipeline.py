from pathlib import Path

from backend.presentation.content.generator import (
    FakePresentationContentGenerator,
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

OUTPUT = Path("experiments/pptx_template/output/" "pipeline_S00122.pptx")

STORAGE = Path("experiments/pptx_template/storage")


pipeline = PptxPresentationPipeline(
    content_generator=(FakePresentationContentGenerator()),
    image_asset_resolver=(LocalImageAssetResolver(STORAGE)),
)

result = pipeline.render(
    spec=spec,
    template_path=TEMPLATE,
    output_path=OUTPUT,
)

print()
print("=" * 80)
print("PPTX PIPELINE COMPLETED")
print("=" * 80)
print(result)
