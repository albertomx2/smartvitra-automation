from pathlib import Path

from backend.commercial.models import (
    BriefCustomer,
    BriefOpening,
    CommercialBrief,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.slides.slide06 import (
    Slide06Renderer,
)

TEMPLATE = Path("experiments/pptx_template/" "input/template2.pptx")


def test_slide06_renders_rooms_table():
    brief = CommercialBrief(
        proposal_number="TEST-006",
        customer=BriefCustomer(
            name="Manolo",
            city="Madrid",
        ),
        openings=[
            BriefOpening(
                opening_id="V1",
                room="Dormitorio",
            ),
            BriefOpening(
                opening_id="V2",
                room="Dormitorio",
            ),
            BriefOpening(
                opening_id="V3",
                room="Salón",
            ),
        ],
    )

    renderer = PowerPointRenderer(TEMPLATE)

    Slide06Renderer().render_structured(
        brief,
        renderer,
    )

    shape = renderer.find_shape("sv_s06_rooms_table")

    table = shape.table

    assert (
        table.cell(
            0,
            0,
        ).text
        == "Dormitorio"
    )

    assert (
        table.cell(
            0,
            1,
        ).text
        == "2"
    )

    assert (
        table.cell(
            1,
            0,
        ).text
        == "Salón"
    )

    assert (
        table.cell(
            1,
            1,
        ).text
        == "1"
    )

    assert (
        table.cell(
            3,
            0,
        ).text
        == "TOTAL"
    )

    assert (
        table.cell(
            3,
            1,
        ).text
        == "3 ventanas"
    )
