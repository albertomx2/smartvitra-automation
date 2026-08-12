from backend.presentation.content.generator import (
    FakePresentationContentGenerator,
)
from backend.presentation.enums import (
    SlideMode,
    SlideType,
)
from backend.presentation.models import (
    PresentationSlide,
    PresentationSpec,
)


def build_spec():
    return PresentationSpec(
        proposal_number="TEST-001",
        customer_name="Test Customer",
        slides=[
            PresentationSlide(
                position=2,
                slide_type=(SlideType.CURRENT_SITUATION),
                mode=SlideMode.DYNAMIC,
                title="Current situation",
                facts={
                    "needs": [
                        {
                            "code": "acoustic_noise",
                        },
                        {
                            "code": "thermal_loss",
                        },
                    ]
                },
            ),
            PresentationSlide(
                position=3,
                slide_type=(SlideType.CONSEQUENCES),
                mode=SlideMode.DYNAMIC,
                title="Consequences",
            ),
        ],
    )


def test_fake_generator_creates_content():
    content = FakePresentationContentGenerator().generate(build_spec())

    shape_names = {item.shape_name for item in content.texts}

    assert "sv_s02_need_1_title" in shape_names

    assert "sv_s02_need_1_body" in shape_names
