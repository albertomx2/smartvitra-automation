from backend.catalog.loader import (
    build_default_catalog,
)

catalog = build_default_catalog()

for product in catalog.list_all():
    print(
        product.model_dump_json(
            indent=2,
        )
    )

    print("-" * 80)
