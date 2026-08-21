from __future__ import annotations

import json

from backend.generation.narration.script.models import (
    NarrationScript,
)
from backend.generation.narration.script.prompts import (
    NARRATION_NATURALNESS_PROMPT,
    NARRATION_SYSTEM_PROMPT,
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
            "fixed_slide_context": {
                "slide04": {
                    "purpose": "installation_and_finish",
                    "known_content": [
                        ("Protección de suelos " "y muebles cercanos"),
                        "Instalación profesional",
                        "Albañilería",
                        "Sellados y nivelación",
                        "Limpieza final",
                    ],
                },
                "slide05": {
                    "purpose": "similar_projects",
                    "description": (
                        "Proyectos similares "
                        "y comparativas visuales "
                        "antes/después."
                    ),
                },
                "slide06": {
                    "purpose": "customer_reviews",
                    "description": ("Reseñas reales mostradas " "en la presentación."),
                    "supported_review_themes": [
                        "profesionalidad",
                        "atención",
                        "cumplimiento",
                        "cuidado",
                        "limpieza",
                        "calidad del trabajo",
                    ],
                },
                "slide08": {
                    "purpose": "good_quality_alternative",
                    "positioning": (
                        "Alternativa de buena " "calidad y menor inversión."
                    ),
                    "pricing_note": (
                        "El presupuesto mostrado "
                        "no corresponde a esta "
                        "alternativa. Elegirla "
                        "permitiría reducir algo "
                        "el importe, pero no existe "
                        "una diferencia exacta "
                        "disponible."
                    ),
                },
                "slide09": {
                    "purpose": "recommended_premium_option",
                    "positioning": ("Opción recomendada de " "mayores prestaciones."),
                    "pricing_note": (
                        "El presupuesto mostrado "
                        "está calculado utilizando "
                        "esta opción."
                    ),
                },
            },
        }

        script = self._llm_client.generate_structured(
            system_prompt=(NARRATION_SYSTEM_PROMPT + NARRATION_NATURALNESS_PROMPT),
            user_prompt=(
                "Genera el guion hablado "
                "completo de esta propuesta "
                "SmartVitra.\n\n"
                "DATOS REALES DISPONIBLES:\n"
                + json.dumps(
                    payload,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            ),
            response_model=NarrationScript,
        )

        script = self._recalculate(
            script,
        )

        NarrationScriptValidator().validate(
            script,
        )

        return script

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
