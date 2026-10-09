from pathlib import Path
from types import SimpleNamespace

from backend.generation.presentation import (
    RealPresentationGenerator,
)
from backend.generation.text_normalization import (
    abbreviate_street_for_geocoding,
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


def test_calle_is_abbreviated_for_geocoding() -> None:
    assert (
        abbreviate_street_for_geocoding("Calle Pablo Vidal 7, Madrid")
        == "C/ Pablo Vidal 7, Madrid"
    )


def test_callejon_is_not_changed_for_geocoding() -> None:
    assert abbreviate_street_for_geocoding("Callejón del Prado 2") == (
        "Callejón del Prado 2"
    )


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


def test_street_view_receives_abbreviated_calle(
    tmp_path: Path,
    monkeypatch,
) -> None:
    snapshot = SimpleNamespace(
        project=SimpleNamespace(
            customer_address="Calle Pablo Vidal 7",
            customer_address2="3º C",
            customer_postal_code="28043",
            customer_city="Madrid",
            customer_country="España",
        )
    )
    received: list[str] = []

    class FakeStreetViewClient:
        def download_facade(self, *, address: str, output_path: Path) -> Path:
            received.append(address)
            return output_path

    monkeypatch.setattr(
        "backend.generation.presentation.GoogleStreetViewFacadeClient",
        FakeStreetViewClient,
    )

    result = RealPresentationGenerator._try_facade(
        snapshot=snapshot,
        work_dir=tmp_path,
    )

    assert result == tmp_path / "cover_facade.jpg"
    assert received == ["C/ Pablo Vidal 7 3º C, 28043 Madrid, España"]
