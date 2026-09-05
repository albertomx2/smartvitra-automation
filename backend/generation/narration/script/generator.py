from __future__ import annotations

import json

from backend.generation.narration.script.fitter import (
    NarrationScriptFitter,
)
from backend.generation.narration.script.fixed import (
    build_fixed_narration_slides,
)
from backend.generation.narration.script.models import (
    NarrationScript,
    NarrationSlide,
    VariableNarrationScript,
)
from backend.generation.narration.script.prompts import (
    VARIABLE_NARRATION_SYSTEM_PROMPT,
)
from backend.generation.narration.script.validator import (
    NarrationScriptValidator,
)
from backend.integrations.llm.models import (
    StructuredLLMClient,
)
from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)


class NarrationScriptGenerator:
    WORDS_PER_MINUTE = 135

    def __init__(
        self,
        llm_client: StructuredLLMClient,
    ) -> None:
        self._llm_client = llm_client

    def generate(
        self,
        *,
        context: dict,
        presentation_content: TemplateV2PresentationContent,
    ) -> NarrationScript:
        payload = {
            "customer_context": context,
            "presentation_content": (
                presentation_content.model_dump(
                    mode="json",
                )
            ),
        }

        variable_script = self._llm_client.generate_structured(
            system_prompt=(VARIABLE_NARRATION_SYSTEM_PROMPT),
            user_prompt=(
                "Genera solo las slides variables 1, 2 y 3.\n\n"
                "DATOS REALES DISPONIBLES:\n"
                + json.dumps(
                    payload,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            ),
            response_model=VariableNarrationScript,
        )

        expected_variable_slides = [1, 2, 3]
        actual_variable_slides = [
            slide.slide_number for slide in variable_script.slides
        ]

        if actual_variable_slides != expected_variable_slides:
            raise ValueError("Gemini narration must contain only slides 1, 2 and 3")

        slides_by_number = {
            slide.slide_number: slide for slide in variable_script.slides
        }

        slides_by_number[7] = self._build_investment_slide(
            context=context,
            presentation_content=presentation_content,
        )

        slides_by_number.update(
            build_fixed_narration_slides(),
        )

        script = NarrationScript(
            estimated_duration_seconds=0,
            word_count=0,
            slides=[slides_by_number[number] for number in range(1, 10)],
        )

        script = NarrationScriptFitter().fit(
            script,
        )

        script = self._recalculate(
            script,
        )

        NarrationScriptValidator().validate(
            script,
        )

        return script

    @staticmethod
    def _build_investment_slide(
        *,
        context: dict,
        presentation_content: TemplateV2PresentationContent,
    ) -> NarrationSlide:
        """Build the price narration without exposing internal product codes."""

        pricing = context.get("pricing") or {}
        total = float(pricing.get("total") or 0)
        formatted_total = (
            f"{total:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        )
        percentage = pricing.get("discount_percentage")
        discount_label = (
            f"del {float(percentage):g} por ciento " if percentage is not None else ""
        )
        if pricing.get("discount_applied"):
            price_sentence = (
                f"El precio final, con el descuento {discount_label}aplicado si nos "
                f"contratas en los próximos 15 días, es de {formatted_total} euros."
            )
        else:
            price_sentence = f"El precio final es de {formatted_total} euros."

        payment_terms = "; ".join(
            term.replace("%", " por ciento").replace("inst.", "instalación")
            for term in presentation_content.slide07.payment_terms
        )
        narration = (
            "Creemos que esta elección de ventanas responde bien a las necesidades "
            "que hemos comentado y es una solución adecuada para mejorar el confort "
            f"de tu vivienda. {price_sentence} La forma de pago es: {payment_terms}. "
            "Este presupuesto corresponde a la opción de mayores prestaciones que "
            "te presentamos a continuación."
        )

        return NarrationSlide(
            slide_number=7,
            commercial_objective="investment",
            estimated_duration_seconds=25,
            narration=narration,
        )

    def _recalculate(
        self,
        script: NarrationScript,
    ) -> NarrationScript:
        word_count = len(script.full_text.split())

        duration = round((word_count / self.WORDS_PER_MINUTE) * 60)

        slides = []

        for slide in script.slides:
            slide_words = len(slide.narration.split())

            slide_duration = max(
                5,
                round((slide_words / self.WORDS_PER_MINUTE) * 60),
            )

            slides.append(
                slide.model_copy(
                    update={
                        "estimated_duration_seconds": slide_duration,
                    }
                )
            )

        return script.model_copy(
            update={
                "word_count": word_count,
                "estimated_duration_seconds": duration,
                "slides": slides,
            }
        )
