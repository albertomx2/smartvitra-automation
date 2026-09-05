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
                "Genera solo las slides variables 1, 2, 3 y 7.\n\n"
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

        expected_variable_slides = [1, 2, 3, 7]
        actual_variable_slides = [
            slide.slide_number for slide in variable_script.slides
        ]

        if actual_variable_slides != expected_variable_slides:
            raise ValueError("Gemini narration must contain only slides 1, 2, 3 and 7")

        slides_by_number = {
            slide.slide_number: slide for slide in variable_script.slides
        }

        self._ensure_discount_message(
            slides_by_number=slides_by_number,
            context=context,
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
    def _ensure_discount_message(
        *,
        slides_by_number: dict,
        context: dict,
    ) -> None:
        """Guarantee the time-limited discount wording independently of Gemini."""

        pricing = context.get("pricing") or {}

        if not pricing.get("discount_applied"):
            return

        slide = slides_by_number[7]

        if "15 días" in slide.narration.lower():
            return

        total = float(pricing.get("total") or 0)
        currency = str(pricing.get("currency") or "€")
        formatted_total = (
            f"{total:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        )

        sentence = (
            "El precio final, con el descuento aplicado si nos contratas "
            f"en los próximos 15 días, es de {formatted_total} {currency}."
        )

        slides_by_number[7] = slide.model_copy(
            update={
                "narration": f"{slide.narration.rstrip()} {sentence}",
            }
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
