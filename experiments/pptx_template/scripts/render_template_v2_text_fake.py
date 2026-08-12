from pathlib import Path

from backend.presentation.content.template_v2_fake import (
    FakeTemplateV2ContentGenerator,
)
from backend.presentation.content.template_v2_normalizer import (
    TemplateV2ContentNormalizer,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_content_renderer import (
    TemplateV2ContentRenderer,
)
from backend.rendering.pptx.template_v2_icon_renderer import (
    TemplateV2IconRenderer,
)

TEMPLATE = Path("experiments/pptx_template/input/" "template.pptx")

OUTPUT = Path("experiments/pptx_template/output/" "template_v2_text_fake.pptx")


content = FakeTemplateV2ContentGenerator().generate()


content = TemplateV2ContentNormalizer().normalize(content)

renderer = PowerPointRenderer(TEMPLATE)

TemplateV2ContentRenderer().render(
    content,
    renderer,
)

TemplateV2IconRenderer().render(
    content,
    renderer,
)

renderer.save(OUTPUT)

print(OUTPUT)
