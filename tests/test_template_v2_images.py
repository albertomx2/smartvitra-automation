from pathlib import Path

from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_image_renderer import (
    TemplateV2ImageRenderer,
)

TEMPLATE = Path("experiments/pptx_template/input/template.pptx")

FAKE_IMAGE = Path("experiments/pptx_template/input/images/problem_test.jpg")


def test_template_v2_image_replacement_preserves_geometry():
    renderer = PowerPointRenderer(TEMPLATE)

    shape = renderer.find_shape("sv_s01_cover_photo")

    original_geometry = (
        shape.left,
        shape.top,
        shape.width,
        shape.height,
    )

    TemplateV2ImageRenderer().render(
        renderer=renderer,
        images={
            "cover_photo": FAKE_IMAGE,
        },
    )

    new_shape = renderer.find_shape("sv_s01_cover_photo")

    new_geometry = (
        new_shape.left,
        new_shape.top,
        new_shape.width,
        new_shape.height,
    )

    assert new_geometry == original_geometry


def test_template_v2_all_image_bindings_can_render():
    renderer = PowerPointRenderer(TEMPLATE)

    images = {
        "cover_photo": FAKE_IMAGE,
        "problem_photo": FAKE_IMAGE,
        "generated_solution": FAKE_IMAGE,
        "project_photo_1": FAKE_IMAGE,
        "project_photo_2": FAKE_IMAGE,
        "project_photo_3": FAKE_IMAGE,
    }

    TemplateV2ImageRenderer().render(
        renderer=renderer,
        images=images,
    )

    for shape_name in (
        "sv_s01_cover_photo",
        "sv_s02_problem_photo",
        "sv_s03_generated_solution_image",
        "sv_s05_project_photo_1",
        "sv_s05_project_photo_2",
        "sv_s05_project_photo_3",
    ):
        assert renderer.find_shape(shape_name).name == shape_name


def test_problem_slide_image_fills_slide_and_removes_legacy_content():
    renderer = PowerPointRenderer(TEMPLATE)

    TemplateV2ImageRenderer().render(
        renderer=renderer,
        images={
            "problem_photo": Path(
                "assets/presentation/problem_variants/noise_heat_cold.png"
            ),
        },
    )

    slide = renderer.presentation.slides[1]
    assert len(slide.shapes) == 1

    picture = slide.shapes[0]
    assert picture.name == "sv_s02_problem_photo"
    assert picture.left == 0
    assert picture.top == 0
    assert picture.width == renderer.presentation.slide_width
    assert picture.height == renderer.presentation.slide_height
