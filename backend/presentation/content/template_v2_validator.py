import re
from dataclasses import dataclass

from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)
from backend.presentation.content.template_v2_constraints import (
    TEMPLATE_V2_TEXT_LIMITS,
)


@dataclass(frozen=True)
class TemplateV2Violation:
    field: str
    reason: str


class TemplateV2ValidationError(ValueError):
    def __init__(
        self,
        violations: list[TemplateV2Violation],
    ) -> None:
        self.violations = violations

        message = "; ".join(
            (f"{violation.field}: " f"{violation.reason}") for violation in violations
        )

        super().__init__(message)


class TemplateV2ContentValidator:
    def validate(
        self,
        content: TemplateV2PresentationContent,
    ) -> None:
        violations: list[TemplateV2Violation] = []

        self._validate_length(
            violations,
            "sv_s01_intro_text",
            content.slide01.intro_text,
        )

        if len(content.slide02.issues) != 5:
            violations.append(
                TemplateV2Violation(
                    field="slide02.issues",
                    reason=("exactly 5 issues " "are required"),
                )
            )

        # Slide 2 uses a full-slide brand image. Its issue descriptions remain
        # available to narration, but no longer have legacy textbox limits.

        for index, solution in enumerate(
            content.slide03.solutions,
            start=1,
        ):
            self._validate_length(
                violations,
                f"sv_s03_solution_{index}",
                solution.text,
            )

        self._validate_length(
            violations,
            "sv_s03_main_benefit",
            content.slide03.main_benefit,
        )

        self._validate_complete_sentence(
            violations,
            "sv_s03_main_benefit",
            content.slide03.main_benefit,
        )

        self._validate_length(
            violations,
            ("sv_s03_" "main_benefit_secondary"),
            content.slide03.secondary_benefit,
        )

        self._validate_complete_sentence(
            violations,
            "sv_s03_main_benefit_secondary",
            content.slide03.secondary_benefit,
        )

        self._validate_length(
            violations,
            "sv_s03_benefit_claim",
            content.slide03.benefit_claim,
        )

        for index, summary in enumerate(
            content.slide07.project_summary,
            start=1,
        ):
            self._validate_length(
                violations,
                f"sv_s07_summary_{index}",
                summary,
            )

        if violations:
            raise TemplateV2ValidationError(violations)

    @staticmethod
    def _validate_complete_sentence(
        violations: list[TemplateV2Violation],
        field: str,
        value: str,
    ) -> None:
        incomplete_endings = {
            "a",
            "al",
            "con",
            "de",
            "del",
            "e",
            "el",
            "en",
            "la",
            "las",
            "los",
            "o",
            "para",
            "por",
            "que",
            "sin",
            "u",
            "un",
            "una",
            "y",
        }

        words = re.findall(
            (r"[A-Za-zÁÉÍÓÚÜÑ" r"áéíóúüñ]+"),
            value,
        )

        if not words:
            return

        last_word = words[-1].lower()

        if last_word in incomplete_endings:
            violations.append(
                TemplateV2Violation(
                    field=field,
                    reason=(
                        "text ends with "
                        "an incomplete "
                        "connector: "
                        f"{last_word!r}"
                    ),
                )
            )

    @staticmethod
    def _validate_length(
        violations: list[TemplateV2Violation],
        field: str,
        value: str,
    ) -> None:
        limit = TEMPLATE_V2_TEXT_LIMITS.get(field)

        if limit is None:
            return

        actual = len(value)

        if actual <= limit:
            return

        violations.append(
            TemplateV2Violation(
                field=field,
                reason=(f"{actual} characters; " f"maximum is {limit}"),
            )
        )
