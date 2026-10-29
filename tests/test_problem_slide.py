from pathlib import Path
from uuid import uuid4

import pytest

from backend.generation.problem_slide import (
    HomeProblem,
    ProblemSlideSelector,
)
from backend.generation.snapshot import (
    CaseGenerationSnapshot,
    GenerationProjectSnapshot,
    GenerationWindowSnapshot,
)


def _snapshot(
    *,
    visit_notes: str | None = None,
    windows: list[tuple[str | None, str | None]] | None = None,
) -> CaseGenerationSnapshot:
    return CaseGenerationSnapshot(
        case_id=uuid4(),
        status="draft",
        visit_notes=visit_notes,
        project=GenerationProjectSnapshot(
            number=1,
            version=1,
            alias_number="TEST-001",
            version_name="Version 1",
            customer_name="Cliente prueba",
            subtotal=1000,
            tax=210,
            final_price=1210,
            currency_symbol="€",
        ),
        windows=[
            GenerationWindowSnapshot(
                id=uuid4(),
                prefweb_item_id=f"item-{index}",
                position=index,
                problem_type=problem_type,
                commercial_notes=notes,
            )
            for index, (problem_type, notes) in enumerate(windows or [], start=1)
        ],
    )


@pytest.mark.parametrize(
    ("visit_notes", "windows", "expected", "filename"),
    [
        (
            "En invierno entra frío, en verano hace calor y hay mucho ruido.",
            [],
            {HomeProblem.COLD, HomeProblem.HEAT, HomeProblem.NOISE},
            "noise_heat_cold.png",
        ),
        (
            "Mucho calor y tráfico durante el verano.",
            [],
            {HomeProblem.HEAT, HomeProblem.NOISE},
            "heat_noise.png",
        ),
        (
            None,
            [("noise", "Se cuela frío en invierno")],
            {HomeProblem.COLD, HomeProblem.NOISE},
            "cold_noise.png",
        ),
        (
            None,
            [("thermal", None)],
            {HomeProblem.COLD, HomeProblem.HEAT},
            "cold_heat.png",
        ),
        (
            None,
            [("noise", None)],
            {HomeProblem.NOISE},
            "noise.png",
        ),
        (
            "La vivienda se sobrecalienta en verano.",
            [],
            {HomeProblem.HEAT},
            "heat.png",
        ),
        (
            None,
            [("air", None)],
            {HomeProblem.COLD},
            "cold.png",
        ),
    ],
)
def test_problem_slide_selector_maps_all_supported_combinations(
    visit_notes: str | None,
    windows: list[tuple[str | None, str | None]],
    expected: set[HomeProblem],
    filename: str,
) -> None:
    selector = ProblemSlideSelector()
    snapshot = _snapshot(visit_notes=visit_notes, windows=windows)

    assert selector.detect(snapshot) == frozenset(expected)
    assert (
        selector.select(snapshot)
        == Path("assets/presentation/problem_variants") / filename
    )


def test_problem_slide_selector_uses_neutral_thermal_fallback() -> None:
    selector = ProblemSlideSelector()

    assert selector.detect(_snapshot()) == frozenset(
        {HomeProblem.COLD, HomeProblem.HEAT}
    )
