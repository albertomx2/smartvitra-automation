from pathlib import Path

from backend.catalog.models import ProductTechnicalData
from backend.catalog.repository import ProductCatalogRepository

DEFAULT_CATALOG_ROOT = Path("assets/catalog")


def load_product(
    product_file: Path,
) -> ProductTechnicalData:
    product = ProductTechnicalData.model_validate_json(
        product_file.read_text(
            encoding="utf-8",
        )
    )

    source_path = product_file.parent / product.source_document

    if not source_path.exists():
        raise FileNotFoundError(
            f"Technical source document not found: " f"{source_path}"
        )

    return product.model_copy(update={"source_document": str(source_path)})


def build_default_catalog(
    catalog_root: Path = DEFAULT_CATALOG_ROOT,
) -> ProductCatalogRepository:
    if not catalog_root.exists():
        raise FileNotFoundError(f"Catalog directory not found: " f"{catalog_root}")

    product_files = sorted(catalog_root.glob("*/product.json"))

    products = [load_product(product_file) for product_file in product_files]

    if not products:
        raise ValueError(f"No products found in catalog: " f"{catalog_root}")

    return ProductCatalogRepository(products)
