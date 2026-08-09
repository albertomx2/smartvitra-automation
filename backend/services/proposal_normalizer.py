from decimal import Decimal

from backend.domain.proposal import (
    Commercial,
    Customer,
    GlassConfiguration,
    Opening,
    PaymentTerms,
    Pricing,
    Proposal,
)
from backend.integrations.pdf.models import (
    RawOpening,
    RawProposalData,
)


class ProposalNormalizer:
    def normalize(
        self,
        raw: RawProposalData,
    ) -> Proposal:
        return Proposal(
            proposal_number=raw.proposal_number,
            proposal_date=raw.proposal_date,
            customer=Customer(
                name=raw.customer_name or "UNKNOWN",
                address=raw.customer_address,
                city=raw.customer_city,
                country=raw.customer_country,
            ),
            commercial=(
                Commercial(
                    name=raw.commercial_name,
                )
                if raw.commercial_name
                else None
            ),
            odoo_quote_id=raw.proposal_number,
            openings=[self._normalize_opening(opening) for opening in raw.openings],
            pricing=self._normalize_pricing(raw),
        )

    def _normalize_opening(
        self,
        raw: RawOpening,
    ) -> Opening:
        return Opening(
            id=raw.identifier,
            position=raw.position,
            room=raw.room,
            window_type=raw.description,
            quantity=1,
            glass=self._normalize_glass(raw.glass_description),
        )

    def _normalize_glass(
        self,
        description: str | None,
    ) -> GlassConfiguration | None:
        if description is None:
            return None

        normalized = description.casefold()

        return GlassConfiguration(
            description=description,
            control_solar=("control solar" in normalized),
            low_emissivity=("bajo emisivo" in normalized),
            argon=("argón" in normalized or "argon" in normalized),
        )

    def _normalize_pricing(
        self,
        raw: RawProposalData,
    ) -> Pricing | None:
        if not self._has_pricing(raw):
            return None

        payment_terms = None

        if raw.payment_terms is not None:
            payment_terms = PaymentTerms(
                description=raw.payment_terms.text,
                deposit_percentage=Decimal(50),
                pre_installation_percentage=Decimal(30),
                final_percentage=Decimal(20),
            )

        return Pricing(
            currency="EUR",
            usual_cost=raw.usual_cost,
            discount_total=raw.discount_total,
            subtotal=raw.subtotal,
            tax_total=raw.tax_total,
            total=raw.total,
            payment_terms=payment_terms,
        )

    def _has_pricing(
        self,
        raw: RawProposalData,
    ) -> bool:
        return any(
            value is not None
            for value in (
                raw.usual_cost,
                raw.discount_total,
                raw.subtotal,
                raw.tax_total,
                raw.total,
            )
        )
