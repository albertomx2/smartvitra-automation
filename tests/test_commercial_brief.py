from backend.catalog.loader import (
    build_default_catalog,
)
from backend.commercial.builder import (
    CommercialBriefBuilder,
)
from backend.domain.proposal import (
    Customer,
    CustomerNeed,
    GlassConfiguration,
    Opening,
    ProductReference,
    Proposal,
)
from backend.matching.benefit_matcher import (
    BenefitMatcher,
)


def test_build_commercial_brief():
    proposal = Proposal(
        proposal_number="TEST-001",
        customer=Customer(
            name="Test Customer",
            city="Madrid",
        ),
        openings=[
            Opening(
                id="V1",
                room="Dormitorio",
                window_type="Ventana 2 hojas",
                glass=GlassConfiguration(
                    description=("Bajo emisivo + argón"),
                    low_emissivity=True,
                    argon=True,
                ),
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
            CustomerNeed(
                code="thermal_loss",
                description=("Entrada de frío."),
                priority=3,
            ),
        ],
    )

    matcher = BenefitMatcher(build_default_catalog())

    matches = matcher.match(proposal)

    builder = CommercialBriefBuilder(build_default_catalog())

    brief = builder.build(
        proposal,
        matches,
    )

    assert brief.proposal_number == "TEST-001"

    assert brief.customer.name == "Test Customer"

    assert brief.primary_need is not None

    assert brief.primary_need.code == "acoustic_noise"

    assert brief.primary_need.covered is True

    assert len(brief.secondary_needs) == 1

    assert brief.secondary_needs[0].code == "thermal_loss"

    assert len(brief.openings) == 1

    assert brief.openings[0].opening_id == "V1"

    assert set(brief.openings[0].product_codes) == {
        "UNIK",
        "THERMOACUSTIC",
    }

    assert len(brief.products) == 2

    assert brief.uncovered_need_codes == []


def test_uncovered_need_is_preserved():
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
                description=("Necesidad de privacidad."),
                priority=5,
            ),
        ],
    )

    matcher = BenefitMatcher(build_default_catalog())

    matches = matcher.match(proposal)

    brief = CommercialBriefBuilder(build_default_catalog()).build(
        proposal,
        matches,
    )

    assert brief.primary_need is not None

    assert brief.primary_need.code == "privacy"

    assert brief.primary_need.covered is False

    assert brief.uncovered_need_codes == ["privacy"]


def test_commercial_brief_preserves_pricing():
    from decimal import Decimal

    from backend.domain.proposal import (
        PaymentTerms,
        Pricing,
    )

    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        pricing=Pricing(
            currency="EUR",
            subtotal=Decimal("1000.00"),
            tax_total=Decimal("210.00"),
            total=Decimal("1210.00"),
            payment_terms=PaymentTerms(description="50 / 30 / 20"),
        ),
    )

    matches = BenefitMatcher(build_default_catalog()).match(proposal)

    brief = CommercialBriefBuilder(build_default_catalog()).build(
        proposal,
        matches,
    )

    assert brief.pricing is not None

    assert brief.pricing.total == Decimal("1210.00")

    assert brief.pricing.payment_terms == "50 / 30 / 20"


def test_commercial_brief_includes_photos():
    from backend.domain.enums import PhotoType
    from backend.domain.proposal import Photo

    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        photos=[
            Photo(
                opening_id="V1",
                photo_type=PhotoType.PROBLEM,
                storage_key="photos/V1/problem.jpg",
                usage=[
                    "current_problem",
                    "before_after",
                ],
                description="Ventana actual",
            )
        ],
    )

    catalog = build_default_catalog()

    matches = BenefitMatcher(catalog).match(proposal)

    brief = CommercialBriefBuilder(catalog).build(
        proposal,
        matches,
    )

    assert len(brief.photos) == 1
    assert brief.photos[0].opening_id == "V1"
    assert brief.photos[0].photo_type == "problem"
    assert brief.photos[0].is_ai_generated is False
    assert "before_after" in brief.photos[0].usage


def test_commercial_brief_includes_technical_properties():
    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        products=[
            ProductReference(
                product_code="UNIK",
                name="UNIK",
            )
        ],
        customer_needs=[
            CustomerNeed(
                code="acoustic_noise",
                description="Ruido exterior.",
                priority=5,
            )
        ],
    )

    catalog = build_default_catalog()

    matches = BenefitMatcher(catalog).match(proposal)

    brief = CommercialBriefBuilder(catalog).build(
        proposal,
        matches,
    )

    assert len(brief.products) == 1

    unik = brief.products[0]

    codes = {item.code for item in unik.technical_properties}

    assert "thermal_transmittance" in codes
    assert "acoustic_insulation" in codes

    assert unik.technical_source == "assets/catalog/unik/source.pdf"


def test_commercial_brief_includes_services():
    from decimal import Decimal

    from backend.domain.proposal import (
        Pricing,
        ServiceLine,
    )

    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        pricing=Pricing(
            services=[
                ServiceLine(
                    name="INSTALACIÓN INCLUIDA",
                    subtotal=Decimal("0.00"),
                )
            ]
        ),
    )

    catalog = build_default_catalog()

    matches = BenefitMatcher(catalog).match(proposal)

    brief = CommercialBriefBuilder(catalog).build(
        proposal,
        matches,
    )

    assert len(brief.services) == 1

    assert brief.services[0].name == "INSTALACIÓN INCLUIDA"

    assert brief.services[0].included is True


def test_commercial_brief_preserves_photo_usage():
    from backend.domain.enums import PhotoType
    from backend.domain.proposal import Photo

    proposal = Proposal(
        customer=Customer(name="Test Customer"),
        photos=[
            Photo(
                opening_id="V1",
                photo_type=PhotoType.PROBLEM,
                storage_key=("photos/V1/problem.jpg"),
                usage=[
                    "current_problem",
                    "problem_confirmation",
                    "before_after",
                ],
            )
        ],
    )

    catalog = build_default_catalog()

    matches = BenefitMatcher(catalog).match(proposal)

    brief = CommercialBriefBuilder(catalog).build(
        proposal,
        matches,
    )

    assert len(brief.photos) == 1

    assert brief.photos[0].usage == [
        "current_problem",
        "problem_confirmation",
        "before_after",
    ]
