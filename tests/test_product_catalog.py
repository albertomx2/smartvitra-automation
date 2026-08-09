from backend.catalog.loader import (
    build_default_catalog,
)


def test_default_catalog_contains_known_products():
    catalog = build_default_catalog()

    unik = catalog.get("UNIK")

    assert unik is not None
    assert unik.name == "UNIK"

    microventilation = catalog.get("MICROVENTILATION")

    assert microventilation is not None

    thermoacustic = catalog.get("THERMOACUSTIC")

    assert thermoacustic is not None


def test_unik_contains_technical_properties():
    catalog = build_default_catalog()

    unik = catalog.get("UNIK")

    assert unik is not None

    property_codes = {item.code for item in unik.properties}

    assert "material" in property_codes
    assert "frame_depth" in property_codes
    assert "thermal_transmittance" in property_codes
    assert "acoustic_insulation" in property_codes
