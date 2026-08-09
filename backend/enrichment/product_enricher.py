from copy import deepcopy

from backend.catalog.repository import (
    ProductCatalogRepository,
)
from backend.domain.proposal import (
    ProductReference,
    Proposal,
)
from backend.enrichment.models import (
    ProposalEnrichmentInput,
)


class ProductEnricher:
    def __init__(
        self,
        catalog: ProductCatalogRepository,
    ) -> None:
        self._catalog = catalog

    def enrich(
        self,
        proposal: Proposal,
        enrichment: ProposalEnrichmentInput,
    ) -> Proposal:
        enriched = deepcopy(proposal)

        product_openings: dict[str, set[str]] = {}

        for selection in enrichment.opening_products:
            self._validate_opening(
                enriched,
                selection.opening_id,
            )

            for product_code in selection.product_codes:
                self._validate_product(product_code)

                product_openings.setdefault(
                    product_code,
                    set(),
                ).add(selection.opening_id)

        for product_code in enrichment.global_product_codes:
            self._validate_product(product_code)

            product_openings.setdefault(
                product_code,
                set(),
            )

        enriched.products = [
            self._build_product_reference(
                product_code,
                opening_ids,
            )
            for product_code, opening_ids in product_openings.items()
        ]

        return enriched

    def _build_product_reference(
        self,
        product_code: str,
        opening_ids: set[str],
    ) -> ProductReference:
        product = self._catalog.get(product_code)

        if product is None:
            raise ValueError(f"Unknown product: {product_code}")

        return ProductReference(
            product_code=product.product_code,
            name=product.name,
            technical_sheet_id=(product.source_document),
            relevant_to_openings=sorted(opening_ids),
        )

    def _validate_product(
        self,
        product_code: str,
    ) -> None:
        if self._catalog.get(product_code) is None:
            raise ValueError(f"Unknown product: {product_code}")

    def _validate_opening(
        self,
        proposal: Proposal,
        opening_id: str,
    ) -> None:
        known_openings = {opening.id for opening in proposal.openings}

        if opening_id not in known_openings:
            raise ValueError(f"Unknown opening: {opening_id}")
