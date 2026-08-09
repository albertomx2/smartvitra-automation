from backend.catalog.loader import (
    build_default_catalog,
)
from backend.domain.proposal import (
    Customer,
    CustomerNeed,
    Opening,
    ProductReference,
    Proposal,
)
from backend.matching.benefit_matcher import (
    BenefitMatcher,
)


def test_match_acoustic_need_with_products():
    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        openings=[
            Opening(
                id="V1",
            ),
        ],
        products=[
            ProductReference(
                product_code="UNIK",
                name="UNIK",
                relevant_to_openings=[
                    "V1",
                ],
            ),
            ProductReference(
                product_code="THERMOACUSTIC",
                name=("Cajón SUMUM Thermoacustic"),
                relevant_to_openings=[
                    "V1",
                ],
            ),
        ],
        customer_needs=[
            CustomerNeed(
                code="acoustic_noise",
                description=("Mucho ruido exterior."),
                priority=5,
            ),
        ],
    )

    matcher = BenefitMatcher(build_default_catalog())

    result = matcher.match(proposal)

    assert len(result.matches) == 1

    acoustic_match = result.matches[0]

    assert acoustic_match.need_code == "acoustic_noise"

    assert acoustic_match.priority == 5

    assert acoustic_match.benefit_categories == ["acoustic"]

    assert len(acoustic_match.matching_products) == 2

    product_codes = {
        product.product_code for product in acoustic_match.matching_products
    }

    assert product_codes == {
        "UNIK",
        "THERMOACUSTIC",
    }


def test_matches_are_sorted_by_need_priority():
    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        products=[
            ProductReference(
                product_code="UNIK",
                name="UNIK",
            ),
        ],
        customer_needs=[
            CustomerNeed(
                code="thermal_loss",
                description=("Pérdida térmica."),
                priority=3,
            ),
            CustomerNeed(
                code="acoustic_noise",
                description=("Ruido exterior."),
                priority=5,
            ),
        ],
    )

    matcher = BenefitMatcher(build_default_catalog())

    result = matcher.match(proposal)

    assert len(result.matches) == 2

    assert result.matches[0].need_code == "acoustic_noise"

    assert result.matches[1].need_code == "thermal_loss"


def test_thermal_need_matches_thermal_benefit():
    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        products=[
            ProductReference(
                product_code="UNIK",
                name="UNIK",
            ),
        ],
        customer_needs=[
            CustomerNeed(
                code="thermal_loss",
                description=("Entrada de frío."),
                priority=4,
            ),
        ],
    )

    matcher = BenefitMatcher(build_default_catalog())

    result = matcher.match(proposal)

    thermal_match = result.matches[0]

    assert thermal_match.benefit_categories == ["thermal"]

    assert len(thermal_match.matching_products) == 1

    benefits = thermal_match.matching_products[0].benefits

    assert benefits[0].category == "thermal"


def test_need_without_matching_product_is_preserved():
    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        products=[
            ProductReference(
                product_code="UNIK",
                name="UNIK",
            ),
        ],
        customer_needs=[
            CustomerNeed(
                code="privacy",
                description=("El cliente quiere más privacidad."),
                priority=4,
            ),
        ],
    )

    matcher = BenefitMatcher(build_default_catalog())

    result = matcher.match(proposal)

    assert len(result.matches) == 1

    privacy_match = result.matches[0]

    assert privacy_match.need_code == "privacy"

    assert privacy_match.matching_products == []

    assert result.uncovered_need_codes == ["privacy"]


def test_ventilation_matches_microventilation():
    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        products=[
            ProductReference(
                product_code="MICROVENTILATION",
                name="Microventilación",
                relevant_to_openings=[
                    "V1",
                ],
            ),
        ],
        customer_needs=[
            CustomerNeed(
                code="ventilation",
                description=("Mejorar ventilación."),
                priority=4,
            ),
        ],
    )

    matcher = BenefitMatcher(build_default_catalog())

    result = matcher.match(proposal)

    ventilation = result.matches[0]

    assert len(ventilation.matching_products) == 1

    product = ventilation.matching_products[0]

    assert product.product_code == "MICROVENTILATION"

    assert product.benefits[0].category == "ventilation"
