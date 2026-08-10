from backend.catalog.repository import (
    ProductCatalogRepository,
)
from backend.domain.proposal import Proposal
from backend.matching.models import (
    BenefitMatchResult,
    MatchedBenefit,
    MatchedProduct,
    NeedProductMatch,
)
from backend.needs.catalog import NEED_DEFINITIONS
from backend.needs.models import CustomerNeedCode


class BenefitMatcher:
    def __init__(
        self,
        catalog: ProductCatalogRepository,
    ) -> None:
        self._catalog = catalog

    def match(
        self,
        proposal: Proposal,
    ) -> BenefitMatchResult:
        matches: list[NeedProductMatch] = []

        sorted_needs = sorted(
            proposal.customer_needs,
            key=lambda need: need.priority or 0,
            reverse=True,
        )

        for need in sorted_needs:
            need_code = CustomerNeedCode(need.code)

            definition = NEED_DEFINITIONS[need_code]

            required_categories = set(definition.benefit_categories)

            matched_products: list[MatchedProduct] = []

            for product_reference in proposal.products:
                product = self._catalog.get(product_reference.product_code)

                if product is None:
                    continue

                matching_benefits = [
                    benefit
                    for benefit in product.benefits
                    if benefit.category in required_categories
                ]

                if not matching_benefits:
                    continue

                matched_products.append(
                    MatchedProduct(
                        product_code=(product.product_code),
                        product_name=product.name,
                        relevant_to_openings=(product_reference.relevant_to_openings),
                        benefits=[
                            MatchedBenefit(
                                benefit_code=(benefit.code),
                                title=benefit.title,
                                category=(benefit.category),
                                description=(benefit.description),
                            )
                            for benefit in matching_benefits
                        ],
                    )
                )

            matches.append(
                NeedProductMatch(
                    need_code=need.code,
                    need_description=(need.description),
                    source_text=need.source_text,
                    priority=(need.priority or 1),
                    benefit_categories=sorted(required_categories),
                    matching_products=(matched_products),
                )
            )

        uncovered_need_codes = [
            match.need_code for match in matches if not match.matching_products
        ]

        return BenefitMatchResult(
            matches=matches,
            uncovered_need_codes=(uncovered_need_codes),
        )
