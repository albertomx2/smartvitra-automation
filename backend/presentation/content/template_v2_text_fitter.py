from __future__ import annotations

import re

from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)
from backend.presentation.content.template_v2_constraints import (
    TEMPLATE_V2_TEXT_LIMITS,
)

_INCOMPLETE_ENDINGS = {
    "a",
    "al",
    "ante",
    "bajo",
    "con",
    "contra",
    "de",
    "del",
    "desde",
    "durante",
    "e",
    "el",
    "en",
    "entre",
    "hacia",
    "hasta",
    "la",
    "las",
    "los",
    "mediante",
    "o",
    "para",
    "por",
    "que",
    "segun",
    "según",
    "sin",
    "sobre",
    "tras",
    "u",
    "un",
    "una",
    "y",
}


def _normalize_text(
    text: str,
) -> str:
    return " ".join(text.split())


def _last_word(
    text: str,
) -> str:
    words = re.findall(
        r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+",
        text,
    )

    if not words:
        return ""

    return words[-1].lower()


def _fit_text(
    text: str,
    maximum: int,
) -> str:
    """
    Generic compact-text fitter.

    Suitable for labels, bullets and short
    non-sentence content.
    """

    value = _normalize_text(text)

    if len(value) <= maximum:
        return value

    shortened = value[:maximum].rstrip()

    if " " in shortened:
        candidate = shortened.rsplit(
            " ",
            1,
        )[0].rstrip()

        if candidate:
            shortened = candidate

    return shortened.rstrip(" ,;:-")


def _fit_sentence(
    text: str,
    maximum: int,
) -> str:
    """
    Fit customer-facing prose without leaving
    a grammatically dangling final connector.
    """

    value = _normalize_text(text)

    if len(value) <= maximum:
        return value

    # First preference:
    # keep a complete sentence already present
    # before the hard limit.
    prefix = value[: maximum + 1]

    sentence_end = max(
        prefix.rfind("."),
        prefix.rfind("!"),
        prefix.rfind("?"),
    )

    if sentence_end >= max(
        20,
        int(maximum * 0.55),
    ):
        return prefix[: sentence_end + 1].strip()

    # Otherwise shorten at a word boundary.
    shortened = value[:maximum].rstrip()

    if " " in shortened:
        shortened = shortened.rsplit(
            " ",
            1,
        )[0].rstrip()

    shortened = shortened.rstrip(" ,;:-")

    words = shortened.split()

    # Remove connectors/articles that would make
    # the resulting sentence obviously incomplete.
    while len(words) > 1 and _last_word(" ".join(words)) in _INCOMPLETE_ENDINGS:
        words.pop()

    result = " ".join(words).rstrip(" ,;:-")

    # Make the shortened result visibly complete.
    if result and result[-1] not in ".!?":
        while len(result) + 1 > maximum and len(words) > 1:
            words.pop()

            while len(words) > 1 and _last_word(" ".join(words)) in _INCOMPLETE_ENDINGS:
                words.pop()

            result = " ".join(words).rstrip(" ,;:-")

        result += "."

    return result


class TemplateV2DeterministicTextFitter:
    def fit(
        self,
        content: TemplateV2PresentationContent,
    ) -> TemplateV2PresentationContent:
        fitted = content.model_copy(
            deep=True,
        )

        fitted.slide01.intro_text = _fit_sentence(
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

        fitted.slide02.impact_statement = _fit_sentence(
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

        fitted.slide03.main_benefit = _fit_sentence(
            fitted.slide03.main_benefit,
            TEMPLATE_V2_TEXT_LIMITS["sv_s03_main_benefit"],
        )

        fitted.slide03.secondary_benefit = _fit_sentence(
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
                fitted.slide07.project_summary[index - 1] = _fit_sentence(
                    summary,
                    TEMPLATE_V2_TEXT_LIMITS[key],
                )

        return fitted
