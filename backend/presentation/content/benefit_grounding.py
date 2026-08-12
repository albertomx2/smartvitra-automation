from backend.presentation.enums import (
    SlideType,
)
from backend.presentation.models import (
    PresentationSpec,
)


def get_allowed_benefit_categories(
    spec: PresentationSpec,
) -> set[str]:
    allowed: set[str] = set()

    benefits_slide = spec.get_slide(SlideType.BENEFITS)

    for benefit in benefits_slide.facts.get(
        "benefits",
        [],
    ):
        category = benefit.get("category")

        if category:
            allowed.add(str(category))

    proposal_slide = spec.get_slide(SlideType.PROPOSAL)

    for opening in proposal_slide.facts.get(
        "openings",
        [],
    ):
        description = (opening.get("glass_description") or "").casefold()

        if "control solar" in description:
            allowed.add("solar_control")

    if allowed.intersection(
        {
            "thermal",
            "acoustic",
            "solar_control",
        }
    ):
        allowed.add("comfort")

    return allowed
