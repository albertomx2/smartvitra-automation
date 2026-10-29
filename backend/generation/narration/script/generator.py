from __future__ import annotations

import json
from copy import deepcopy

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
from backend.generation.text_normalization import (
    expand_street_abbreviations,
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
        payload = self._build_variable_payload(
            context=context,
            presentation_content=presentation_content,
        )

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

        variable_script = variable_script.model_copy(
            update={
                "slides": [
                    slide.model_copy(
                        update={
                            "narration": expand_street_abbreviations(
                                slide.narration,
                            )
                        }
                    )
                    for slide in variable_script.slides
                ]
            }
        )

        slides_by_number = {
            slide.slide_number: slide for slide in variable_script.slides
        }

        slides_by_number[6] = self._build_investment_slide(
            context=context,
            presentation_content=presentation_content,
        )
        slides_by_number[7] = self._build_alternatives_slide(
            context=context,
        )

        slides_by_number.update(
            build_fixed_narration_slides(),
        )

        script = NarrationScript(
            estimated_duration_seconds=0,
            word_count=0,
            slides=[slides_by_number[number] for number in range(1, 11)],
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
    def _build_variable_payload(
        *,
        context: dict,
        presentation_content: TemplateV2PresentationContent,
    ) -> dict:
        """Keep technical product identifiers out of Gemini's spoken copy."""

        narration_context = deepcopy(context)

        customer = narration_context.get("customer")
        if isinstance(customer, dict):
            for key in ("address", "address2"):
                value = customer.get(key)
                if isinstance(value, str):
                    customer[key] = expand_street_abbreviations(value)

        proposal = narration_context.get("proposal")
        if isinstance(proposal, dict):
            openings = proposal.get("openings")
            if isinstance(openings, list):
                allowed_opening_fields = {
                    "room",
                    "quantity",
                    "commercial_notes",
                }
                proposal["openings"] = [
                    {
                        key: value
                        for key, value in opening.items()
                        if key in allowed_opening_fields
                    }
                    for opening in openings
                    if isinstance(opening, dict)
                ]

        visible_content = presentation_content.model_dump(
            mode="json",
        )
        visible_content.pop("slide07", None)

        slide03 = visible_content.get("slide03")
        if isinstance(slide03, dict):
            slide03.pop("solutions", None)

        return {
            "customer_context": narration_context,
            "presentation_content": visible_content,
        }

    @staticmethod
    def _build_investment_slide(
        *,
        context: dict,
        presentation_content: TemplateV2PresentationContent,
    ) -> NarrationSlide:
        """Build the price narration without exposing internal product codes."""

        pricing = context.get("pricing") or {}
        total = float(pricing.get("total") or 0)
        formatted_total = NarrationScriptGenerator._format_spoken_amount(total)
        project_summary = NarrationScriptGenerator._build_project_summary(context)
        narration = (
            "Para esta propuesta hemos seleccionado Thermofibra como solución "
            f"principal. {project_summary} Su combinación de fibra de vidrio en la "
            "hoja, refuerzo térmico en el marco y triple junta ayuda a mejorar el "
            f"aislamiento y el confort interior. Con este material, el importe "
            f"total, con IVA incluido, es de {formatted_total} euros. La forma "
            "de pago figura en el documento "
            "de aceptación."
        )

        return NarrationSlide(
            slide_number=6,
            commercial_objective="investment",
            estimated_duration_seconds=25,
            narration=narration,
        )

    @staticmethod
    def _build_alternatives_slide(
        *,
        context: dict,
    ) -> NarrationSlide:
        pricing = context.get("pricing") or {}
        total = float(pricing.get("total") or 0)
        cortizo_total = total * 0.85
        refine_total = total * 1.10

        narration = (
            "Además, SmartVitra ofrece dos alternativas con materiales distintos. "
            "Cortizo A setenta reduce la inversión un quince por ciento frente a "
            f"Thermofibra, hasta {NarrationScriptGenerator._format_spoken_amount(cortizo_total)} "
            "euros, con un aislamiento térmico inferior. Refine incrementa la "
            f"inversión un diez por ciento, hasta {NarrationScriptGenerator._format_spoken_amount(refine_total)} "
            "euros, y aporta hoja oculta, una estética más limpia y mayor superficie "
            "acristalada. Ambos importes incluyen IVA y mantienen la misma forma de pago."
        )

        return NarrationSlide(
            slide_number=7,
            commercial_objective="material_alternatives",
            estimated_duration_seconds=25,
            narration=narration,
        )

    @staticmethod
    def _build_project_summary(context: dict) -> str:
        proposal = context.get("proposal") or {}
        openings = proposal.get("openings") or []

        quantities: list[int] = []
        rooms: list[str] = []

        for opening in openings:
            if not isinstance(opening, dict):
                continue

            try:
                quantities.append(max(1, int(opening.get("quantity") or 1)))
            except (TypeError, ValueError):
                quantities.append(1)

            room = opening.get("room")
            if isinstance(room, str) and room.strip() and room.strip() not in rooms:
                rooms.append(room.strip())

        total_openings = sum(quantities)

        if total_openings <= 0:
            return "La configuración responde a las necesidades que hemos comentado."

        noun = "ventana" if total_openings == 1 else "ventanas"
        room_text = ""
        if rooms:
            room_text = " para " + ", ".join(rooms[:3])

        return f"La propuesta incluye {total_openings} {noun}{room_text}."

    @staticmethod
    def _format_spoken_amount(value: float) -> str:
        rounded = round(value)
        return f"{rounded:,}".replace(",", ".")

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
