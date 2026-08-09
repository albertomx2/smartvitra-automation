import pytest

from backend.catalog.loader import (
    build_default_catalog,
)
from backend.domain.proposal import (
    Customer,
    Opening,
    Proposal,
)
from backend.enrichment.models import (
    OpeningProductSelection,
    ProposalEnrichmentInput,
)
from backend.enrichment.product_enricher import (
    ProductEnricher,
)


def test_enrich_proposal_with_products():
    proposal = Proposal(
        proposal_number="TEST-001",
        customer=Customer(name="Test Customer"),
        openings=[
            Opening(
                id="V1",
                position=1,
            ),
            Opening(
                id="V2",
                position=2,
            ),
        ],
    )

    enrichment = ProposalEnrichmentInput(
        opening_products=[
            OpeningProductSelection(
                opening_id="V1",
                product_codes=[
                    "UNIK",
                    "MICROVENTILATION",
                ],
            ),
            OpeningProductSelection(
                opening_id="V2",
                product_codes=[
                    "UNIK",
                ],
            ),
        ],
        global_product_codes=[
            "THERMOACUSTIC",
        ],
    )

    catalog = build_default_catalog()

    enricher = ProductEnricher(catalog)

    enriched = enricher.enrich(
        proposal,
        enrichment,
    )

    assert len(enriched.products) == 3

    unik = next(
        product for product in enriched.products if product.product_code == "UNIK"
    )

    assert unik.relevant_to_openings == [
        "V1",
        "V2",
    ]

    microventilation = next(
        product
        for product in enriched.products
        if product.product_code == "MICROVENTILATION"
    )

    assert microventilation.relevant_to_openings == ["V1"]

    thermoacustic = next(
        product
        for product in enriched.products
        if product.product_code == "THERMOACUSTIC"
    )

    assert thermoacustic.relevant_to_openings == []


def test_unknown_product_is_rejected():
    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        openings=[
            Opening(
                id="V1",
            ),
        ],
    )

    enrichment = ProposalEnrichmentInput(
        opening_products=[
            OpeningProductSelection(
                opening_id="V1",
                product_codes=[
                    "NON_EXISTENT",
                ],
            ),
        ],
    )

    enricher = ProductEnricher(build_default_catalog())

    with pytest.raises(
        ValueError,
        match="Unknown product",
    ):
        enricher.enrich(
            proposal,
            enrichment,
        )


def test_unknown_opening_is_rejected():
    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        openings=[
            Opening(
                id="V1",
            ),
        ],
    )

    enrichment = ProposalEnrichmentInput(
        opening_products=[
            OpeningProductSelection(
                opening_id="V99",
                product_codes=[
                    "UNIK",
                ],
            ),
        ],
    )

    enricher = ProductEnricher(build_default_catalog())

    with pytest.raises(
        ValueError,
        match="Unknown opening",
    ):
        enricher.enrich(
            proposal,
            enrichment,
        )
