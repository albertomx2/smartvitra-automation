from backend.domain.enums import PhotoType
from backend.domain.proposal import (
    CustomerNeed,
    Photo,
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

        known_opening_ids = {opening.id for opening in enriched.openings}

        for photo in enrichment.photos:
            if (
                photo.opening_id is not None
                and photo.opening_id not in known_opening_ids
            ):
                raise ValueError("Unknown opening in photo: " f"{photo.opening_id}")

        enriched.photos = [
            Photo(
                opening_id=photo.opening_id,
                photo_type=PhotoType(photo.photo_type),
                storage_key=photo.storage_key,
                usage=photo.usage,
                description=photo.description,
                original_filename=photo.original_filename,
            )
            for photo in enrichment.photos
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
