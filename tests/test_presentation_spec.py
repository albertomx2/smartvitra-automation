from backend.catalog.loader import (
    build_default_catalog,
)
from backend.commercial.builder import (
    CommercialBriefBuilder,
)
from backend.domain.enums import PhotoType
from backend.domain.proposal import (
    Customer,
    CustomerNeed,
    Opening,
    Photo,
    ProductReference,
    Proposal,
)
from backend.matching.benefit_matcher import (
    BenefitMatcher,
)
from backend.presentation.builder import (
    PresentationSpecBuilder,
)
from backend.presentation.enums import (
    SlideMode,
    SlideType,
)


def build_test_spec():
    catalog = build_default_catalog()

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
        ],
        customer_needs=[
            CustomerNeed(
                code="acoustic_noise",
                description="Ruido exterior.",
                priority=5,
                source_text=("Lo peor es el ruido."),
            ),
        ],
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
            ),
        ],
    )

    matches = BenefitMatcher(catalog).match(proposal)

    brief = CommercialBriefBuilder(catalog).build(
        proposal,
        matches,
    )

    return PresentationSpecBuilder().build(brief)


def test_presentation_contains_12_slides():
    spec = build_test_spec()

    assert len(spec.slides) == 12

    assert [slide.position for slide in spec.slides] == list(range(1, 13))


def test_slide_types_follow_canonical_order():
    spec = build_test_spec()

    assert [slide.slide_type for slide in spec.slides] == [
        SlideType.COVER,
        SlideType.CURRENT_SITUATION,
        SlideType.CONSEQUENCES,
        SlideType.PROBLEM_CONFIRMATION,
        SlideType.SOLUTION_TRANSITION,
        SlideType.PROPOSAL,
        SlideType.BENEFITS,
        SlideType.BEFORE_AFTER,
        SlideType.WHY_SMARTVITRA,
        SlideType.INVESTMENT,
        SlideType.FINAL_PRICE,
        SlideType.CLOSING,
    ]


def test_fixed_slides_are_locked():
    spec = build_test_spec()

    fixed_types = {
        SlideType.COVER,
        SlideType.SOLUTION_TRANSITION,
        SlideType.WHY_SMARTVITRA,
        SlideType.CLOSING,
    }

    for slide_type in fixed_types:
        slide = spec.get_slide(slide_type)

        assert slide.mode == SlideMode.FIXED
        assert slide.locked is True
        assert slide.template_key is not None


def test_current_situation_contains_customer_need():
    spec = build_test_spec()

    slide = spec.get_slide(SlideType.CURRENT_SITUATION)

    needs = slide.facts["needs"]

    assert len(needs) == 1

    assert needs[0]["code"] == "acoustic_noise"

    assert needs[0]["source_text"] == "Lo peor es el ruido."

    assert slide.requires_ai_text is True


def test_problem_confirmation_selects_correct_photo():
    spec = build_test_spec()

    slide = spec.get_slide(SlideType.PROBLEM_CONFIRMATION)

    assert len(slide.photos) == 1

    assert slide.photos[0].opening_id == "V1"

    assert slide.photos[0].role == "problem_confirmation"


def test_before_after_requests_generated_image():
    spec = build_test_spec()

    slide = spec.get_slide(SlideType.BEFORE_AFTER)

    assert len(slide.photos) == 1

    assert slide.photos[0].role == "before_after"

    assert slide.requires_generated_image is True

    assert slide.facts["generation_status"] == "pending"


def test_proposal_slide_contains_real_products():
    spec = build_test_spec()

    slide = spec.get_slide(SlideType.PROPOSAL)

    products = slide.facts["products"]

    assert len(products) == 1

    assert products[0]["product_code"] == "UNIK"


def test_benefits_slide_uses_matched_benefits():
    spec = build_test_spec()

    slide = spec.get_slide(SlideType.BENEFITS)

    benefits = slide.facts["benefits"]

    assert len(benefits) >= 1

    codes = {benefit["code"] for benefit in benefits}

    assert "acoustic" in codes
