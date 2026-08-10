from backend.integrations.gamma.prompt_builder import (
    GammaPromptBuilder,
)
from backend.presentation.enums import (
    SlideMode,
    SlideType,
)
from backend.presentation.models import (
    PresentationSlide,
    PresentationSpec,
)


def test_gamma_prompt_contains_all_slides():
    spec = PresentationSpec(
        proposal_number="S00122",
        customer_name="Test Customer",
        slides=[
            PresentationSlide(
                position=position,
                slide_type=slide_type,
                mode=SlideMode.DYNAMIC,
                title=f"Slide {position}",
            )
            for position, slide_type in enumerate(
                SlideType,
                start=1,
            )
        ],
    )

    prompt = GammaPromptBuilder().build(spec)

    assert "Customer: Test Customer" in prompt
    assert "Proposal: S00122" in prompt

    for position in range(1, 13):
        assert f"## SLIDE {position:02d}" in prompt

    assert "Keep exactly 12 cards" in prompt


def test_gamma_prompt_marks_locked_slide():
    spec = PresentationSpec(
        customer_name="Test Customer",
        slides=[
            PresentationSlide(
                position=1,
                slide_type=SlideType.COVER,
                mode=SlideMode.FIXED,
                title="SmartVitra",
                locked=True,
            )
        ],
    )

    prompt = GammaPromptBuilder().build(spec)

    assert "LOCKED:" in prompt
    assert "Do not rewrite" in prompt
