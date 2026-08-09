from backend.catalog.models import (
    ProductTechnicalData,
)


class ProductCatalogRepository:
    def __init__(
        self,
        products: list[ProductTechnicalData],
    ) -> None:
        self._products = {product.product_code: product for product in products}

    def get(
        self,
        product_code: str,
    ) -> ProductTechnicalData | None:
        return self._products.get(product_code)

    def list_all(
        self,
    ) -> list[ProductTechnicalData]:
        return list(self._products.values())
