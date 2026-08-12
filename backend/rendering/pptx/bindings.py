from dataclasses import dataclass

from backend.presentation.enums import (
    SlideType,
)


@dataclass(frozen=True)
class ImageBinding:
    slide_type: SlideType

    photo_role: str

    shape_name: str


IMAGE_BINDINGS = (
    ImageBinding(
        slide_type=(SlideType.PROBLEM_CONFIRMATION),
        photo_role="problem_confirmation",
        shape_name="sv_s04_problem_photo",
    ),
    ImageBinding(
        slide_type=(SlideType.BEFORE_AFTER),
        photo_role="before_after",
        shape_name="sv_s08_before_photo",
    ),
)


@dataclass(frozen=True)
class SemanticCardBinding:
    outer_shape: str
    accent_shape: str


SEMANTIC_CARD_BINDINGS = {
    "s02_need_1": SemanticCardBinding(
        outer_shape="Rectángulo 3",
        accent_shape="Rectángulo 4",
    ),
    "s02_need_2": SemanticCardBinding(
        outer_shape="Rectángulo 7",
        accent_shape="Rectángulo 8",
    ),
    "s02_need_3": SemanticCardBinding(
        outer_shape="Rectángulo 5",
        accent_shape="Rectángulo 6",
    ),
    "s02_need_4": SemanticCardBinding(
        outer_shape="Rectángulo 9",
        accent_shape="Rectángulo 10",
    ),
}


BENEFIT_ICON_BINDINGS = {
    1: "sv_s07_benefit_1_icon",
    2: "sv_s07_benefit_2_icon",
    3: "sv_s07_benefit_3_icon",
    4: "sv_s07_benefit_4_icon",
}
