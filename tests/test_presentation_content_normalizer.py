from backend.presentation.content.models import (
    GeneratedPresentationContent,
)
from backend.presentation.content.normalizer import (
    PresentationContentNormalizer,
)


def test_normalizer_orders_benefit_icons():
    from backend.presentation.content.models import (
        BenefitIconContent,
    )

    content = GeneratedPresentationContent(
        benefit_icons=[
            BenefitIconContent(
                benefit_index=4,
                category="comfort",
                icon_key="comfort",
            ),
            BenefitIconContent(
                benefit_index=2,
                category="acoustic",
                icon_key="acoustic",
            ),
            BenefitIconContent(
                benefit_index=1,
                category="thermal",
                icon_key="thermal",
            ),
            BenefitIconContent(
                benefit_index=3,
                category="solar_control",
                icon_key="solar_control",
            ),
        ]
    )

    normalized = PresentationContentNormalizer().normalize(content)

    assert [item.benefit_index for item in normalized.benefit_icons] == [
        1,
        2,
        3,
        4,
    ]
