from types import SimpleNamespace

from backend.generation.presentation import (
    RealPresentationGenerator,
)
from backend.generation.text_normalization import (
    expand_street_abbreviations,
)


def test_street_abbreviation_is_expanded() -> None:
    assert (
        expand_street_abbreviations(
            "C/ Pablo Vidal 7, 3º C",
        )
        == "Calle Pablo Vidal 7, 3º C"
    )


def test_street_abbreviation_without_space_is_expanded() -> None:
    assert expand_street_abbreviations("c/Alcalá 1") == "Calle Alcalá 1"


def test_presentation_address_expands_street_abbreviation() -> None:
    snapshot = SimpleNamespace(
        project=SimpleNamespace(
            customer_address="C/ Pablo Vidal 7",
            customer_address2="3º C",
            customer_postal_code="28043",
            customer_city="Madrid",
            customer_country="España",
        )
    )

    assert RealPresentationGenerator._build_address(snapshot) == (
        "Calle Pablo Vidal 7 3º C, 28043 Madrid, España"
    )
