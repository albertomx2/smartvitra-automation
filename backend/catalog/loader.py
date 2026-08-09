from backend.catalog.models import (
    ProductBenefit,
    ProductTechnicalData,
    TechnicalProperty,
)
from backend.catalog.repository import (
    ProductCatalogRepository,
)


def build_default_catalog() -> ProductCatalogRepository:
    products = [
        ProductTechnicalData(
            product_code="UNIK",
            name="UNIK",
            category="window_profile",
            source_document=("assets/catalog/unik/source.pdf"),
            properties=[
                TechnicalProperty(
                    code="material",
                    name="Material",
                    value="PVC",
                ),
                TechnicalProperty(
                    code="frame_depth",
                    name="Profundidad del marco",
                    value=76,
                    unit="mm",
                ),
                TechnicalProperty(
                    code="thermal_transmittance",
                    name="Transmitancia térmica Uf",
                    value="0.88",
                    unit="W/m²K",
                ),
                TechnicalProperty(
                    code="acoustic_insulation",
                    name="Aislamiento acústico",
                    value="hasta 48",
                    unit="dB",
                ),
            ],
            benefits=[
                ProductBenefit(
                    code="thermal",
                    title="Aislamiento térmico",
                    category="thermal",
                ),
                ProductBenefit(
                    code="acoustic",
                    title="Aislamiento acústico",
                    category="acoustic",
                ),
            ],
        ),
        ProductTechnicalData(
            product_code="MICROVENTILATION",
            name="Microventilación",
            category="hardware",
            source_document=("assets/catalog/microventilacion/source.pdf"),
            benefits=[
                ProductBenefit(
                    code="controlled_ventilation",
                    title="Ventilación controlada",
                    category="ventilation",
                ),
            ],
        ),
        ProductTechnicalData(
            product_code="THERMOACUSTIC",
            name="Cajón SUMUM Thermoacustic",
            category="shutter_box",
            source_document=("assets/catalog/thermoacustic/source.pdf"),
            benefits=[
                ProductBenefit(
                    code="thermal",
                    title="Aislamiento térmico",
                    category="thermal",
                ),
                ProductBenefit(
                    code="acoustic",
                    title="Aislamiento acústico",
                    category="acoustic",
                ),
            ],
        ),
    ]

    return ProductCatalogRepository(products)
