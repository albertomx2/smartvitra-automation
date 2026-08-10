from backend.catalog.repository import ProductCatalogRepository
from backend.commercial.models import (
    BriefBenefit,
    BriefCustomer,
    BriefNeed,
    BriefOpening,
    BriefPhoto,
    BriefPricing,
    BriefProduct,
    BriefService,
    BriefTechnicalProperty,
    CommercialBrief,
)
from backend.domain.proposal import Proposal
from backend.matching.models import (
    BenefitMatchResult,
)


class CommercialBriefBuilder:
    def __init__(
        self,
        catalog: ProductCatalogRepository,
    ) -> None:
        self._catalog = catalog

    def build(
        self,
        proposal: Proposal,
        matches: BenefitMatchResult,
    ) -> CommercialBrief:
        needs = self._build_needs(matches)

        primary_need = needs[0] if needs else None

        secondary_needs = needs[1:] if len(needs) > 1 else []

        return CommercialBrief(
            proposal_number=proposal.proposal_number,
            customer=BriefCustomer(
                name=proposal.customer.name,
                city=proposal.customer.city,
            ),
            primary_need=primary_need,
            secondary_needs=secondary_needs,
            openings=self._build_openings(proposal),
            products=self._build_products(matches),
            pricing=self._build_pricing(proposal),
            photos=self._build_photos(proposal),
            services=self._build_services(proposal),
            uncovered_need_codes=(matches.uncovered_need_codes),
        )

    def _build_needs(
        self,
        matches: BenefitMatchResult,
    ) -> list[BriefNeed]:
        return [
            BriefNeed(
                code=match.need_code,
                description=match.need_description,
                priority=match.priority,
                covered=bool(match.matching_products),
                source_text=match.source_text,
            )
            for match in matches.matches
        ]

    def _build_openings(
        self,
        proposal: Proposal,
    ) -> list[BriefOpening]:
        result: list[BriefOpening] = []

        for opening in proposal.openings:
            product_codes = [
                product.product_code
                for product in proposal.products
                if opening.id in product.relevant_to_openings
            ]

            glass_description = None

            if opening.glass is not None:
                glass_description = opening.glass.description

            result.append(
                BriefOpening(
                    opening_id=opening.id,
                    room=opening.room,
                    window_type=opening.window_type,
                    glass_description=glass_description,
                    product_codes=product_codes,
                )
            )

        return result

    def _build_products(
        self,
        matches: BenefitMatchResult,
    ) -> list[BriefProduct]:
        products: dict[str, BriefProduct] = {}

        for match in matches.matches:
            for matched_product in match.matching_products:
                product = products.get(matched_product.product_code)

                if product is None:
                    catalog_product = self._catalog.get(matched_product.product_code)

                    technical_properties = []
                    technical_source = None

                    if catalog_product is not None:
                        technical_properties = [
                            BriefTechnicalProperty(
                                code=property_.code,
                                name=property_.name,
                                value=property_.value,
                                unit=property_.unit,
                            )
                            for property_ in catalog_product.properties
                        ]

                        technical_source = catalog_product.source_document

                    product = BriefProduct(
                        product_code=(matched_product.product_code),
                        product_name=(matched_product.product_name),
                        relevant_to_openings=(matched_product.relevant_to_openings),
                        technical_properties=technical_properties,
                        technical_source=technical_source,
                    )

                    products[matched_product.product_code] = product

                existing_codes = {benefit.code for benefit in product.benefits}

                for benefit in matched_product.benefits:
                    if benefit.benefit_code in existing_codes:
                        continue

                    product.benefits.append(
                        BriefBenefit(
                            code=(benefit.benefit_code),
                            title=benefit.title,
                            category=benefit.category,
                            description=(benefit.description),
                        )
                    )

                    existing_codes.add(benefit.benefit_code)

        return list(products.values())

    def _build_photos(
        self,
        proposal: Proposal,
    ) -> list[BriefPhoto]:
        return [
            BriefPhoto(
                photo_id=str(photo.id),
                opening_id=photo.opening_id,
                photo_type=photo.photo_type.value,
                storage_key=photo.storage_key,
                usage=photo.usage,
                description=photo.description,
                is_ai_generated=photo.is_ai_generated,
            )
            for photo in proposal.photos
        ]

    def _build_services(
        self,
        proposal: Proposal,
    ) -> list[BriefService]:
        if proposal.pricing is None:
            return []

        return [
            BriefService(
                name=service.name,
                description=service.description,
                included=(service.subtotal is not None and service.subtotal == 0),
            )
            for service in proposal.pricing.services
        ]

    def _build_pricing(
        self,
        proposal: Proposal,
    ) -> BriefPricing | None:
        if proposal.pricing is None:
            return None

        payment_terms = None

        if proposal.pricing.payment_terms is not None:
            payment_terms = proposal.pricing.payment_terms.description

        return BriefPricing(
            currency=proposal.pricing.currency,
            usual_cost=proposal.pricing.usual_cost,
            discount_total=proposal.pricing.discount_total,
            subtotal=proposal.pricing.subtotal,
            tax_total=proposal.pricing.tax_total,
            total=proposal.pricing.total,
            payment_terms=payment_terms,
        )
