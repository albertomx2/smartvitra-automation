from backend.commercial.models import (
    BriefOpening,
)
from backend.presentation.structured.rooms import (
    build_rooms_table,
)


def test_rooms_are_grouped():
    openings = [
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
    ]

    result = build_rooms_table(openings)

    assert result.total_quantity == 3

    quantities = {row.label: row.quantity for row in result.rows}

    assert quantities["Dormitorio"] == 2
    assert quantities["Salón"] == 1


def test_too_many_rooms_are_consolidated():
    openings = [
        BriefOpening(
            opening_id="V1",
            room="Dormitorio",
        ),
        BriefOpening(
            opening_id="V2",
            room="Salón",
        ),
        BriefOpening(
            opening_id="V3",
            room="Cocina",
        ),
        BriefOpening(
            opening_id="V4",
            room="Despacho",
        ),
    ]

    result = build_rooms_table(openings)

    assert len(result.rows) == 3

    assert result.total_quantity == 4

    assert any(row.label == "Otras estancias" for row in result.rows)
