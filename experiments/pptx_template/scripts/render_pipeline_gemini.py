from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.llm.gemini import (
    GeminiStructuredClient,
)
from backend.presentation.content.generator import (
    LLMPresentationContentGenerator,
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

load_dotenv(dotenv_path=Path(".env"))


TEMPLATE = Path("experiments/pptx_template/input/" "template.pptx")

OUTPUT = Path("experiments/pptx_template/output/" "pipeline_S00122_gemini.pptx")

STORAGE = Path("experiments/pptx_template/storage")


llm_client = GeminiStructuredClient()

generator = LLMPresentationContentGenerator(llm_client)

pipeline = PptxPresentationPipeline(
    content_generator=generator,
    image_asset_resolver=(LocalImageAssetResolver(STORAGE)),
)

result = pipeline.render(
    spec=spec,
    template_path=TEMPLATE,
    output_path=OUTPUT,
)

print()
print("=" * 80)
print("REAL AI PPTX PIPELINE COMPLETED")
print("=" * 80)
print(result)
