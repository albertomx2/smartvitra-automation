from pathlib import Path

import pytest

from backend.catalog.loader import (
    build_default_catalog,
    load_product,
)
from backend.catalog.models import (
    ProductTechnicalData,
)
from backend.catalog.repository import (
    ProductCatalogRepository,
)


def test_default_catalog_contains_known_products():
    catalog = build_default_catalog()

    products = catalog.list_all()

    assert len(products) == 3

    assert catalog.get("UNIK") is not None
    assert catalog.get("MICROVENTILATION") is not None
    assert catalog.get("THERMOACUSTIC") is not None


def test_unik_contains_technical_properties():
    catalog = build_default_catalog()

    unik = catalog.get("UNIK")

    assert unik is not None

    property_codes = {item.code for item in unik.properties}

    assert "material" in property_codes
    assert "frame_depth" in property_codes
    assert "thermal_transmittance" in property_codes
    assert "acoustic_insulation" in property_codes


def test_product_source_document_exists():
    catalog = build_default_catalog()

    for product in catalog.list_all():
        assert Path(product.source_document).exists()


def test_load_product_from_json():
    product = load_product(Path("assets/catalog/unik/product.json"))

    assert product.product_code == "UNIK"
    assert product.name == "UNIK"


def test_duplicate_product_codes_are_rejected():
    first = ProductTechnicalData(
        product_code="TEST",
        name="Test 1",
        category="test",
        source_document="test.pdf",
    )

    second = ProductTechnicalData(
        product_code="TEST",
        name="Test 2",
        category="test",
        source_document="test.pdf",
    )

    with pytest.raises(
        ValueError,
        match="Duplicate product code",
    ):
        ProductCatalogRepository(
            [
                first,
                second,
            ]
        )
