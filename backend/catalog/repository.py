from backend.catalog.models import (
    ProductTechnicalData,
)


class ProductCatalogRepository:
    def __init__(
        self,
        products: list[ProductTechnicalData],
    ) -> None:
        self._products: dict[
            str,
            ProductTechnicalData,
        ] = {}

        for product in products:
            if product.product_code in self._products:
                raise ValueError("Duplicate product code: " f"{product.product_code}")

            self._products[product.product_code] = product

    def get(
        self,
        product_code: str,
    ) -> ProductTechnicalData | None:
        return self._products.get(product_code)

    def list_all(
        self,
    ) -> list[ProductTechnicalData]:
        return list(self._products.values())
