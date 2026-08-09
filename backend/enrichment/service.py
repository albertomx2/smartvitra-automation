from backend.domain.proposal import (
    CustomerNeed,
    Proposal,
)
from backend.enrichment.models import (
    ProposalEnrichmentInput,
)
from backend.enrichment.product_enricher import (
    ProductEnricher,
)
from backend.needs.models import (
    CustomerNeedSelection,
)
from backend.needs.service import (
    CustomerNeedsService,
)


class ProposalEnrichmentService:
    def __init__(
        self,
        product_enricher: ProductEnricher,
        customer_needs_service: CustomerNeedsService,
    ) -> None:
        self._product_enricher = product_enricher
        self._customer_needs_service = customer_needs_service

    def enrich(
        self,
        proposal: Proposal,
        enrichment: ProposalEnrichmentInput,
    ) -> Proposal:
        enriched = self._product_enricher.enrich(
            proposal,
            enrichment,
        )

        validated_needs = self._customer_needs_service.validate(
            enrichment.customer_needs
        )

        enriched.customer_needs = [
            self._build_customer_need(selection) for selection in validated_needs
        ]

        return enriched

    def _build_customer_need(
        self,
        selection: CustomerNeedSelection,
    ) -> CustomerNeed:
        definition = self._customer_needs_service.get_definition(selection)

        return CustomerNeed(
            code=selection.code.value,
            description=(selection.description or definition.description),
            priority=selection.priority,
            source_text=selection.source_text,
        )
