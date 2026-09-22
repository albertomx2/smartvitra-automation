import uuid

from backend.generation.snapshot import (
    CaseGenerationSnapshot,
    GenerationItemSnapshot,
    GenerationProjectSnapshot,
    GenerationWindowSnapshot,
)
from backend.generation.technical_sheets import TechnicalSheetSelector


def _snapshot(
    *,
    windows: list[GenerationWindowSnapshot],
    items: list[GenerationItemSnapshot] | None = None,
) -> CaseGenerationSnapshot:
    return CaseGenerationSnapshot(
        case_id=uuid.uuid4(),
        status="draft",
        project=GenerationProjectSnapshot(
            number=100,
            version=1,
            alias_number="2026/100",
            version_name="Version 1",
            customer_name="Cliente",
            subtotal=1000,
            tax=21,
            final_price=1210,
            currency_symbol="€",
        ),
        windows=windows,
        items=items or [],
    )


def _window(description: str, *, position: int = 1) -> GenerationWindowSnapshot:
    return GenerationWindowSnapshot(
        id=uuid.uuid4(),
        prefweb_item_id=f"window-{position}",
        position=position,
        description=description,
    )


def test_selects_both_unik_and_microventilation_for_tilt_turn() -> None:
    snapshot = _snapshot(windows=[_window("Ventana oscilobatiente 2 hojas")])

    filenames = [sheet.filename for sheet in TechnicalSheetSelector().select(snapshot)]

    assert filenames == [
        "Ficha tecnica Microventilacion.pdf",
        "Ficha tecnica UNIK.pdf",
    ]


def test_selects_islide_for_sliding_windows() -> None:
    snapshot = _snapshot(windows=[_window("Corredera iSlide de 3 hojas")])

    filenames = [sheet.filename for sheet in TechnicalSheetSelector().select(snapshot)]

    assert filenames == ["Ficha tecnica iSlide.pdf"]


def test_selects_thermoacustic_when_prefweb_items_include_shutter() -> None:
    snapshot = _snapshot(
        windows=[_window("Ventana 2 hojas")],
        items=[
            GenerationItemSnapshot(
                id_pos="2",
                description="Cajón de persiana incluido",
                item_type="Article",
            )
        ],
    )

    filenames = [sheet.filename for sheet in TechnicalSheetSelector().select(snapshot)]

    assert filenames == [
        "Ficha tecnica Cajon SUMUM Thermoacustic.pdf",
        "Ficha tecnica Microventilacion.pdf",
        "Ficha tecnica UNIK.pdf",
    ]


def test_each_sheet_is_added_only_once_for_repeated_window_types() -> None:
    snapshot = _snapshot(
        windows=[
            _window("Ventana corredera de 2 hojas", position=1),
            _window("Ventana corredera de 3 hojas", position=2),
        ]
    )

    selected = TechnicalSheetSelector().select(snapshot)

    assert [sheet.filename for sheet in selected] == ["Ficha tecnica iSlide.pdf"]
