from pathlib import Path

from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_image_renderer import (
    TemplateV2ImageRenderer,
)

TEMPLATE = Path("experiments/pptx_template/input/" "template.pptx")

OUTPUT = Path("experiments/pptx_template/output/" "template_v2_images_fake.pptx")

FAKE_IMAGE = Path("experiments/pptx_template/input/" "images/problem_test.jpg")


renderer = PowerPointRenderer(TEMPLATE)

images = {
    "cover_photo": FAKE_IMAGE,
    "problem_photo": FAKE_IMAGE,
    "generated_solution": FAKE_IMAGE,
    "project_photo_1": FAKE_IMAGE,
    "project_photo_2": FAKE_IMAGE,
    "project_photo_3": FAKE_IMAGE,
    "generated_result": FAKE_IMAGE,
}

TemplateV2ImageRenderer().render(
    renderer=renderer,
    images=images,
)

renderer.save(OUTPUT)

print(OUTPUT)
