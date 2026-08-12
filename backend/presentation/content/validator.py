from dataclasses import dataclass

from backend.presentation.content.constraints import (
    REQUIRED_SEMANTIC_SLOTS,
    REQUIRED_TEXT_SHAPES,
    TEXT_MAX_CHARACTERS,
)
from backend.presentation.content.models import (
    GeneratedPresentationContent,
)


@dataclass(frozen=True)
class ContentViolation:
    field: str
    reason: str


class PresentationContentValidationError(ValueError):
    def __init__(
        self,
        violations: list[ContentViolation],
    ) -> None:
        self.violations = violations

        message = "; ".join(
            (f"{violation.field}: " f"{violation.reason}") for violation in violations
        )

        super().__init__(message)


class PresentationContentValidator:
    def validate(
        self,
        content: GeneratedPresentationContent,
        *,
        allowed_benefit_categories: set[str] | None = None,
    ) -> None:
        violations: list[ContentViolation] = []

        text_shape_list = [item.shape_name for item in content.texts]

        if len(text_shape_list) != len(set(text_shape_list)):
            violations.append(
                ContentViolation(
                    field="texts",
                    reason="duplicate text fields",
                )
            )

        actual_text_shapes = set(text_shape_list)

        required_text_shapes = set(REQUIRED_TEXT_SHAPES)

        for shape_name in sorted(required_text_shapes - actual_text_shapes):
            violations.append(
                ContentViolation(
                    field=shape_name,
                    reason="required field missing",
                )
            )

        for shape_name in sorted(actual_text_shapes - required_text_shapes):
            violations.append(
                ContentViolation(
                    field=shape_name,
                    reason="unknown editable field",
                )
            )

        for text_content in content.texts:
            max_characters = TEXT_MAX_CHARACTERS.get(text_content.shape_name)

            if max_characters is None:
                continue

            actual_length = len(text_content.text)

            if actual_length > max_characters:
                violations.append(
                    ContentViolation(
                        field=text_content.shape_name,
                        reason=(
                            f"{actual_length} characters; "
                            f"maximum is "
                            f"{max_characters}"
                        ),
                    )
                )

        semantic_slot_list = [item.slot for item in content.semantic_colors]

        if len(semantic_slot_list) != len(set(semantic_slot_list)):
            violations.append(
                ContentViolation(
                    field="semantic_colors",
                    reason=("duplicate semantic slots"),
                )
            )

        actual_slots = set(semantic_slot_list)

        required_slots = set(REQUIRED_SEMANTIC_SLOTS)

        for slot in sorted(required_slots - actual_slots):
            violations.append(
                ContentViolation(
                    field=slot,
                    reason="semantic slot missing",
                )
            )

        for slot in sorted(actual_slots - required_slots):
            violations.append(
                ContentViolation(
                    field=slot,
                    reason="unknown semantic slot",
                )
            )

        if content.slide06 is None:
            violations.append(
                ContentViolation(
                    field="slide06",
                    reason="required structured content missing",
                )
            )

        if content.slide08 is None:
            violations.append(
                ContentViolation(
                    field="slide08",
                    reason="required structured content missing",
                )
            )
        else:
            before_length = len(content.slide08.before_text)

            after_length = len(content.slide08.after_text)

            if before_length > TEXT_MAX_CHARACTERS["sv_s08_before_text"]:
                violations.append(
                    ContentViolation(
                        field="slide08.before_text",
                        reason=(
                            f"{before_length} characters; "
                            "maximum is "
                            f"{TEXT_MAX_CHARACTERS['sv_s08_before_text']}"
                        ),
                    )
                )

            if after_length > TEXT_MAX_CHARACTERS["sv_s08_after_text"]:
                violations.append(
                    ContentViolation(
                        field="slide08.after_text",
                        reason=(
                            f"{after_length} characters; "
                            "maximum is "
                            f"{TEXT_MAX_CHARACTERS['sv_s08_after_text']}"
                        ),
                    )
                )

        if content.slide11 is None:
            violations.append(
                ContentViolation(
                    field="slide11",
                    reason="required structured content missing",
                )
            )
        else:
            tip_length = len(content.slide11.tip_text)

            if tip_length > TEXT_MAX_CHARACTERS["sv_s11_tip_text"]:
                violations.append(
                    ContentViolation(
                        field="slide11.tip_text",
                        reason=(
                            f"{tip_length} characters; "
                            "maximum is "
                            f"{TEXT_MAX_CHARACTERS['sv_s11_tip_text']}"
                        ),
                    )
                )

        benefit_indices = [
            benefit_icon.benefit_index for benefit_icon in content.benefit_icons
        ]

        expected_indices = {
            1,
            2,
            3,
            4,
        }

        actual_indices = set(benefit_indices)

        if len(benefit_indices) != len(actual_indices):
            violations.append(
                ContentViolation(
                    field="benefit_icons",
                    reason="duplicate benefit indices",
                )
            )

        missing_indices = expected_indices - actual_indices

        extra_indices = actual_indices - expected_indices

        if missing_indices:
            violations.append(
                ContentViolation(
                    field="benefit_icons",
                    reason=(
                        "missing benefit indices: "
                        + ", ".join(str(value) for value in sorted(missing_indices))
                    ),
                )
            )

        if extra_indices:
            violations.append(
                ContentViolation(
                    field="benefit_icons",
                    reason=(
                        "unknown benefit indices: "
                        + ", ".join(str(value) for value in sorted(extra_indices))
                    ),
                )
            )

        for benefit_icon in content.benefit_icons:
            if (
                allowed_benefit_categories is not None
                and benefit_icon.category not in allowed_benefit_categories
            ):
                allowed_text = ", ".join(sorted(allowed_benefit_categories))

                violations.append(
                    ContentViolation(
                        field=("benefit_icons." f"{benefit_icon.benefit_index}"),
                        reason=(
                            "unsupported benefit category; " f"allowed: {allowed_text}"
                        ),
                    )
                )

            if benefit_icon.category != benefit_icon.icon_key:
                violations.append(
                    ContentViolation(
                        field=("benefit_icons." f"{benefit_icon.benefit_index}"),
                        reason=("category and icon_key " "must match"),
                    )
                )

        if violations:
            raise (PresentationContentValidationError(violations))
