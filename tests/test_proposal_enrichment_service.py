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
from backend.enrichment.service import (
    ProposalEnrichmentService,
)
from backend.needs.models import (
    CustomerNeedCode,
    CustomerNeedSelection,
)
from backend.needs.service import (
    CustomerNeedsService,
)


def test_enrich_proposal_with_products_and_needs():
    proposal = Proposal(
        proposal_number="TEST-001",
        customer=Customer(name="Test Customer"),
        openings=[
            Opening(
                id="V1",
                position=1,
            ),
        ],
    )

    enrichment = ProposalEnrichmentInput(
        opening_products=[
            OpeningProductSelection(
                opening_id="V1",
                product_codes=[
                    "UNIK",
                    "THERMOACUSTIC",
                ],
            ),
        ],
        customer_needs=[
            CustomerNeedSelection(
                code=(CustomerNeedCode.ACOUSTIC_NOISE),
                priority=5,
                description=("Mucho ruido procedente de la calle."),
                source_text=("Lo que más me preocupa es " "el ruido de la avenida."),
            ),
            CustomerNeedSelection(
                code=CustomerNeedCode.THERMAL_LOSS,
                priority=3,
                description=("Entrada de frío durante el invierno."),
            ),
        ],
    )

    service = ProposalEnrichmentService(
        product_enricher=ProductEnricher(build_default_catalog()),
        customer_needs_service=(CustomerNeedsService()),
    )

    enriched = service.enrich(
        proposal,
        enrichment,
    )

    assert len(enriched.products) == 2

    assert len(enriched.customer_needs) == 2

    assert enriched.customer_needs[0].code == "acoustic_noise"

    assert enriched.customer_needs[0].priority == 5

    assert enriched.customer_needs[1].code == "thermal_loss"

    assert enriched.customer_needs[1].priority == 3


def test_original_proposal_is_not_modified():
    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        openings=[
            Opening(
                id="V1",
            ),
        ],
    )

    enrichment = ProposalEnrichmentInput(
        customer_needs=[
            CustomerNeedSelection(
                code=(CustomerNeedCode.ACOUSTIC_NOISE),
                priority=5,
            ),
        ],
    )

    service = ProposalEnrichmentService(
        product_enricher=ProductEnricher(build_default_catalog()),
        customer_needs_service=(CustomerNeedsService()),
    )

    enriched = service.enrich(
        proposal,
        enrichment,
    )

    assert proposal.customer_needs == []

    assert len(enriched.customer_needs) == 1


def test_enrichment_input_can_be_loaded_from_json():
    from pathlib import Path

    path = Path("tests/fixtures/visits/" "example_noise_thermal.json")

    enrichment = ProposalEnrichmentInput.model_validate_json(
        path.read_text(encoding="utf-8")
    )

    assert len(enrichment.customer_needs) == 2

    assert enrichment.customer_needs[0].code == CustomerNeedCode.ACOUSTIC_NOISE

    assert enrichment.customer_needs[0].priority == 5


def test_visit_photos_are_added_to_proposal():
    from pathlib import Path

    path = Path("tests/fixtures/visits/" "example_noise_thermal.json")

    enrichment = ProposalEnrichmentInput.model_validate_json(
        path.read_text(encoding="utf-8")
    )

    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        openings=[
            Opening(id="V1"),
            Opening(id="V2"),
        ],
    )

    service = ProposalEnrichmentService(
        product_enricher=ProductEnricher(build_default_catalog()),
        customer_needs_service=(CustomerNeedsService()),
    )

    enriched = service.enrich(
        proposal,
        enrichment,
    )

    assert len(enriched.photos) == 3

    assert enriched.photos[0].opening_id == "V1"

    assert enriched.photos[0].photo_type.value == "problem"

    assert enriched.photos[2].opening_id is None

    assert enriched.photos[2].photo_type.value == "facade"


def test_photo_with_unknown_opening_is_rejected():
    from backend.enrichment.models import (
        VisitPhotoInput,
    )

    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        openings=[
            Opening(id="V1"),
        ],
    )

    enrichment = ProposalEnrichmentInput(
        photos=[
            VisitPhotoInput(
                opening_id="V99",
                photo_type="problem",
                storage_key="photos/problem.jpg",
            )
        ]
    )

    service = ProposalEnrichmentService(
        product_enricher=ProductEnricher(build_default_catalog()),
        customer_needs_service=(CustomerNeedsService()),
    )

    import pytest

    with pytest.raises(
        ValueError,
        match="Unknown opening in photo",
    ):
        service.enrich(
            proposal,
            enrichment,
        )
