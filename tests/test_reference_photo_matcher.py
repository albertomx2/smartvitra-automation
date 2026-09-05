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
