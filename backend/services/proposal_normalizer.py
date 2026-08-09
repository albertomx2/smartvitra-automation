from decimal import Decimal

from backend.domain.proposal import (
    AdvancePayment,
    Commercial,
    CommercialDiscount,
    Customer,
    GlassConfiguration,
    Opening,
    PaymentTerms,
    PriceLine,
    Pricing,
    Proposal,
    ServiceLine,
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
            lines=[
                PriceLine(
                    opening_id=opening.identifier,
                    description=opening.description or opening.identifier,
                    quantity=opening.quantity or Decimal(1),
                    list_price=opening.list_price,
                    unit_price=opening.discounted_unit_price,
                    discount_percentage=opening.discount_percentage,
                    subtotal=opening.subtotal,
                    tax_percentage=opening.tax_percentage,
                )
                for opening in raw.openings
            ],
            services=[
                ServiceLine(
                    name=service.name,
                    description=service.description,
                    quantity=service.quantity,
                    list_price=service.list_price,
                    unit_price=service.discounted_unit_price,
                    discount_percentage=service.discount_percentage,
                    subtotal=service.subtotal,
                    tax_percentage=service.tax_percentage,
                )
                for service in raw.services
            ],
            discounts=[
                CommercialDiscount(
                    name=discount.name,
                    description=discount.description,
                    amount=discount.amount,
                )
                for discount in raw.discounts
            ],
            advance_payments=[
                AdvancePayment(
                    reference=payment.reference,
                    payment_date=payment.payment_date,
                    amount=payment.amount,
                )
                for payment in raw.advance_payments
            ],
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
