import uuid

from backend.generation.snapshot import GenerationWindowSnapshot
from backend.reference_photos.matcher import (
    ReferencePhotoCandidate,
    ReferencePhotoMatcher,
)


def _photo(
    identifier: str,
    *,
    system: str,
    leaves: str,
    quality: int = 8,
) -> ReferencePhotoCandidate:
    return ReferencePhotoCandidate(
        id=identifier,
        problem_tags=[],
        room_tags=[],
        window_type_tags=[],
        feature_tags=[],
        element_type="window",
        opening_system=system,
        leaf_configuration=leaves,
        quality_score=quality,
    )


def test_exact_system_and_leaf_count_outrank_generic_quality() -> None:
    window = GenerationWindowSnapshot(
        id=uuid.uuid4(),
        prefweb_item_id="one",
        position=1,
        description="Ventana corredera de 3 hojas",
    )
    photos = [
        _photo("wrong-leaves", system="sliding", leaves="two_leaves", quality=10),
        _photo("exact", system="sliding", leaves="three_leaves", quality=6),
        _photo("wrong-system", system="tilt_turn", leaves="three_leaves", quality=10),
    ]

    ranked = ReferencePhotoMatcher().rank_for_window(window=window, photos=photos)

    assert ranked[0].photo.id == "exact"
    assert ranked[0].score > ranked[1].score


def test_islide_is_treated_as_sliding() -> None:
    assert (
        ReferencePhotoMatcher._infer_opening_system("Corredera Islide 2 hojas")
        == "sliding"
    )


def test_generic_window_is_treated_as_tilt_turn() -> None:
    assert (
        ReferencePhotoMatcher._infer_opening_system("Ventana 2 hojas Ref. 2203V")
        == "tilt_turn"
    )


def test_partial_leaf_match_outranks_fixed_only_window() -> None:
    window = GenerationWindowSnapshot(
        id=uuid.uuid4(),
        prefweb_item_id="one",
        position=1,
        description="Ventana 2 hojas + fijo inferior",
    )
    photos = [
        _photo("fixed-only", system="fixed", leaves="other", quality=10),
        _photo("two-leaves", system="tilt_turn", leaves="two_leaves", quality=6),
    ]

    ranked = ReferencePhotoMatcher().rank_for_window(window=window, photos=photos)

    assert ranked[0].photo.id == "two-leaves"
    assert ranked[0].score > ranked[1].score


def test_accessory_design_rows_are_not_matchable_windows() -> None:
    window = GenerationWindowSnapshot(
        id=uuid.uuid4(),
        prefweb_item_id="one",
        position=1,
        reference="CHAPA ALU 2P",
        description="Chapa de aluminio + 2 Pliegues",
    )

    assert ReferencePhotoMatcher().is_matchable_window(window) is False


def test_representative_targets_prioritize_distinct_configurations() -> None:
    from backend.reference_photos.service import ReferencePhotoService

    windows = [
        GenerationWindowSnapshot(
            id=uuid.uuid4(),
            prefweb_item_id="two",
            position=1,
            description="Ventana 2 hojas",
            quantity=2,
        ),
        GenerationWindowSnapshot(
            id=uuid.uuid4(),
            prefweb_item_id="one",
            position=2,
            description="Ventana 1 hoja",
            quantity=3,
        ),
        GenerationWindowSnapshot(
            id=uuid.uuid4(),
            prefweb_item_id="accessory",
            position=3,
            description="Chapa de aluminio + 2 Pliegues",
            quantity=9,
        ),
        GenerationWindowSnapshot(
            id=uuid.uuid4(),
            prefweb_item_id="fixed",
            position=4,
            description="Ventana 2 hojas + fijo lateral",
        ),
    ]

    targets = ReferencePhotoService._representative_targets(
        windows=windows,
        matcher=ReferencePhotoMatcher(),
        limit=3,
    )

    assert [target.prefweb_item_id for target in targets] == [
        "two",
        "one",
        "fixed",
    ]
