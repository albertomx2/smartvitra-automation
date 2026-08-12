from pathlib import Path

from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)

TEMPLATE = Path("experiments/pptx_template/input/template2.pptx")


def test_set_text_preserves_font_size():
    renderer = PowerPointRenderer(TEMPLATE)

    shape = renderer.find_shape("sv_s02_need_1_body")

    paragraph = shape.text_frame.paragraphs[0]

    original_size = paragraph.runs[0].font.size

    renderer.set_text_preserving_style(
        "sv_s02_need_1_body",
        "Texto nuevo de prueba.",
    )

    shape = renderer.find_shape("sv_s02_need_1_body")

    paragraph = shape.text_frame.paragraphs[0]

    new_size = paragraph.runs[0].font.size

    assert new_size == original_size


def test_long_text_is_flagged():
    renderer = PowerPointRenderer(TEMPLATE)

    result = renderer.set_text_preserving_style(
        "sv_s02_need_1_body",
        "A" * 120,
        max_characters=80,
    )

    assert result.estimated_too_long is True


def test_semantic_border_color_is_applied():
    from backend.rendering.pptx.models import (
        SemanticColor,
    )
    from backend.rendering.pptx.renderer import (
        SEMANTIC_COLORS,
    )

    renderer = PowerPointRenderer(TEMPLATE)

    renderer.set_shape_border_color(
        "Rectángulo 5",
        SemanticColor.POSITIVE,
    )

    shape = renderer.find_shape("Rectángulo 5")

    assert shape.line.color.rgb == SEMANTIC_COLORS[SemanticColor.POSITIVE]


def test_replace_picture_preserves_exact_geometry():
    renderer = PowerPointRenderer(TEMPLATE)

    image_path = Path("experiments/pptx_template/input/" "images/problem_test.jpg")

    shape = renderer.find_shape("sv_s04_problem_photo")

    before = (
        shape.left,
        shape.top,
        shape.width,
        shape.height,
    )

    renderer.replace_picture(
        "sv_s04_problem_photo",
        image_path,
    )

    shape = renderer.find_shape("sv_s04_problem_photo")

    after = (
        shape.left,
        shape.top,
        shape.width,
        shape.height,
    )

    assert after == before


def test_replace_picture_preserves_shape_name():
    renderer = PowerPointRenderer(TEMPLATE)

    image_path = Path("experiments/pptx_template/input/" "images/problem_test.jpg")

    renderer.replace_picture(
        "sv_s04_problem_photo",
        image_path,
    )

    shape = renderer.find_shape("sv_s04_problem_photo")

    assert shape.name == "sv_s04_problem_photo"


def test_local_image_asset_resolver():
    from backend.rendering.pptx.assets import (
        LocalImageAssetResolver,
    )

    resolver = LocalImageAssetResolver(Path("experiments/pptx_template/" "storage"))

    path = resolver.resolve("visits/S00122/photos/" "V1/problem_01.jpg")

    assert path.exists()


def test_text_replacement_preserves_run_properties_xml():
    renderer = PowerPointRenderer(TEMPLATE)

    shape = renderer.find_shape("sv_s02_need_1_title")

    run = shape.text_frame.paragraphs[0].runs[0]

    before_rpr = run._r.rPr.xml if run._r.rPr is not None else None

    renderer.set_text_preserving_style(
        "sv_s02_need_1_title",
        "Ruido exterior",
        max_characters=80,
    )

    updated_shape = renderer.find_shape("sv_s02_need_1_title")

    updated_run = updated_shape.text_frame.paragraphs[0].runs[0]

    after_rpr = updated_run._r.rPr.xml if updated_run._r.rPr is not None else None

    assert after_rpr == before_rpr


def test_text_replacement_preserves_shape_geometry():
    renderer = PowerPointRenderer(TEMPLATE)

    shape = renderer.find_shape("sv_s02_need_1_title")

    before = (
        shape.left,
        shape.top,
        shape.width,
        shape.height,
    )

    renderer.set_text_preserving_style(
        "sv_s02_need_1_title",
        "Ruido exterior",
        max_characters=80,
    )

    updated = renderer.find_shape("sv_s02_need_1_title")

    after = (
        updated.left,
        updated.top,
        updated.width,
        updated.height,
    )

    assert after == before


def test_text_replacement_preserves_shape_line_xml():
    renderer = PowerPointRenderer(TEMPLATE)

    shape = renderer.find_shape("sv_s02_need_1_title")

    before = shape._element.spPr.ln.xml if shape._element.spPr.ln is not None else None

    renderer.set_text_preserving_style(
        "sv_s02_need_1_title",
        "Ruido exterior",
        max_characters=80,
    )

    updated = renderer.find_shape("sv_s02_need_1_title")

    after = (
        updated._element.spPr.ln.xml if updated._element.spPr.ln is not None else None
    )

    assert after == before


def test_semantic_slot_colors_complete_card():
    from backend.presentation.content.models import (
        GeneratedPresentationContent,
        SemanticColorContent,
    )
    from backend.rendering.pptx.content_renderer import (
        PresentationContentRenderer,
    )
    from backend.rendering.pptx.models import (
        SemanticColor,
    )
    from backend.rendering.pptx.renderer import (
        SEMANTIC_COLORS,
    )

    renderer = PowerPointRenderer(TEMPLATE)

    content = GeneratedPresentationContent(
        semantic_colors=[
            SemanticColorContent(
                slot="s02_need_2",
                semantic_color=(SemanticColor.PROBLEM_HIGH),
            )
        ]
    )

    PresentationContentRenderer().render(
        content,
        renderer,
    )

    outer = renderer.find_shape("Rectángulo 7")

    accent = renderer.find_shape("Rectángulo 8")

    expected = SEMANTIC_COLORS[SemanticColor.PROBLEM_HIGH]

    assert outer.line.color.rgb == expected
    assert accent.fill.fore_color.rgb == expected


def test_semantic_card_uses_same_color_for_border_and_accent():
    from backend.presentation.content.models import (
        GeneratedPresentationContent,
        SemanticColorContent,
    )
    from backend.rendering.pptx.content_renderer import (
        PresentationContentRenderer,
    )
    from backend.rendering.pptx.models import (
        SemanticColor,
    )
    from backend.rendering.pptx.renderer import (
        SEMANTIC_COLORS,
    )

    renderer = PowerPointRenderer(TEMPLATE)

    content = GeneratedPresentationContent(
        semantic_colors=[
            SemanticColorContent(
                slot="s02_need_3",
                semantic_color=(SemanticColor.WARNING),
            )
        ]
    )

    PresentationContentRenderer().render(
        content,
        renderer,
    )

    outer = renderer.find_shape("Rectángulo 5")

    accent = renderer.find_shape("Rectángulo 6")

    expected = SEMANTIC_COLORS[SemanticColor.WARNING]

    assert outer.line.color.rgb == expected

    assert accent.fill.fore_color.rgb == expected


def test_table_cell_text_can_be_replaced():
    renderer = PowerPointRenderer(TEMPLATE)

    renderer.set_table_cell_text(
        "sv_s06_rooms_table",
        1,
        0,
        "Dormitorio",
    )

    shape = renderer.find_shape("sv_s06_rooms_table")

    assert (
        shape.table.cell(
            1,
            0,
        ).text
        == "Dormitorio"
    )


def test_benefit_icon_renderer_replaces_dynamic_icons():
    from backend.presentation.content.models import (
        BenefitIconContent,
        GeneratedPresentationContent,
    )
    from backend.rendering.pptx.benefit_icon_renderer import (
        BenefitIconRenderer,
    )

    renderer = PowerPointRenderer(TEMPLATE)

    shape = renderer.find_shape("sv_s07_benefit_1_icon")

    before_geometry = (
        shape.left,
        shape.top,
        shape.width,
        shape.height,
    )

    content = GeneratedPresentationContent(
        benefit_icons=[
            BenefitIconContent(
                benefit_index=1,
                category="security",
                icon_key="security",
            )
        ]
    )

    BenefitIconRenderer().render(
        content,
        renderer,
    )

    shape = renderer.find_shape("sv_s07_benefit_1_icon")

    after_geometry = (
        shape.left,
        shape.top,
        shape.width,
        shape.height,
    )

    assert after_geometry == before_geometry
    assert shape.name == "sv_s07_benefit_1_icon"
