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
    value = " ".join(text.split())

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
    value = " ".join(text.split())

    dangling_words = {
        "a",
        "al",
        "con",
        "de",
        "del",
        "donde",
        "e",
        "el",
        "en",
        "la",
        "las",
        "los",
        "o",
        "para",
        "por",
        "porque",
        "que",
        "sin",
        "su",
        "sus",
        "tu",
        "tus",
        "y",
    }

    def close_sentence(
        candidate: str,
    ) -> str:
        words = candidate.rstrip(" ,;:-.!?").split()

        while words and words[-1].lower() in dangling_words:
            words.pop()

        result = " ".join(words).rstrip(" ,;:-")

        if not result:
            return ""

        if result[-1] not in ".!?":
            result += "."

        return result

    # Aunque la frase quepa, rechazamos
    # finales gramaticalmente colgantes.
    if len(value) <= maximum:
        last_word = value.rstrip(" ,;:-.!?").split()[-1].lower()

        if last_word not in dangling_words:
            return value

        return close_sentence(value)

    shortened = value[:maximum].rstrip()

    best_sentence_end = max(
        shortened.rfind("."),
        shortened.rfind("!"),
        shortened.rfind("?"),
    )

    # Si ya existe una oración completa razonablemente
    # larga, preferimos conservarla completa.
    if best_sentence_end >= int(maximum * 0.55):
        shortened = shortened[: best_sentence_end + 1].strip()
    elif " " in shortened:
        shortened = shortened.rsplit(
            " ",
            1,
        )[0].rstrip()

    return close_sentence(shortened)


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
