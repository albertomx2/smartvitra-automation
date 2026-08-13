from __future__ import annotations

from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)
from backend.presentation.content.template_v2_constraints import (
    TEMPLATE_V2_TEXT_LIMITS,
)


def _fit_text(
    text: str,
    maximum: int,
) -> str:
    value = " ".join(text.split())

    if len(value) <= maximum:
        return value

    shortened = value[:maximum].rstrip()

    if " " in shortened:
        candidate = shortened.rsplit(" ", 1)[0].rstrip()

        if candidate:
            shortened = candidate

    return shortened.rstrip(" ,;:-")


class TemplateV2DeterministicTextFitter:
    def fit(
        self,
        content: TemplateV2PresentationContent,
    ) -> TemplateV2PresentationContent:
        fitted = content.model_copy(deep=True)

        fitted.slide01.intro_text = _fit_text(
            fitted.slide01.intro_text,
            TEMPLATE_V2_TEXT_LIMITS["sv_s01_intro_text"],
        )

        for index, issue in enumerate(
            fitted.slide02.issues,
            start=1,
        ):
            key = f"sv_s02_issue_{index}"

            if key in TEMPLATE_V2_TEXT_LIMITS:
                issue.detail = _fit_text(
                    issue.detail,
                    TEMPLATE_V2_TEXT_LIMITS[key],
                )

        fitted.slide02.impact_statement = _fit_text(
            fitted.slide02.impact_statement,
            TEMPLATE_V2_TEXT_LIMITS["sv_s02_issue_6"],
        )

        for index, solution in enumerate(
            fitted.slide03.solutions,
            start=1,
        ):
            key = f"sv_s03_solution_{index}"

            if key in TEMPLATE_V2_TEXT_LIMITS:
                solution.text = _fit_text(
                    solution.text,
                    TEMPLATE_V2_TEXT_LIMITS[key],
                )

        fitted.slide03.main_benefit = _fit_text(
            fitted.slide03.main_benefit,
            TEMPLATE_V2_TEXT_LIMITS["sv_s03_main_benefit"],
        )

        fitted.slide03.secondary_benefit = _fit_text(
            fitted.slide03.secondary_benefit,
            TEMPLATE_V2_TEXT_LIMITS["sv_s03_main_benefit_secondary"],
        )

        fitted.slide03.benefit_claim = _fit_text(
            fitted.slide03.benefit_claim,
            TEMPLATE_V2_TEXT_LIMITS["sv_s03_benefit_claim"],
        )

        for index, summary in enumerate(
            fitted.slide07.project_summary,
            start=1,
        ):
            key = f"sv_s07_summary_{index}"

            if key in TEMPLATE_V2_TEXT_LIMITS:
                fitted.slide07.project_summary[index - 1] = _fit_text(
                    summary,
                    TEMPLATE_V2_TEXT_LIMITS[key],
                )

        return fitted
