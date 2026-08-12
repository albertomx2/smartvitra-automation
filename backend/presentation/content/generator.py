from typing import Protocol

from backend.presentation.content.benefit_grounding import (
    get_allowed_benefit_categories,
)
from backend.presentation.content.corrector import (
    PresentationContentCorrector,
)
from backend.presentation.content.models import (
    GeneratedPresentationContent,
)
from backend.presentation.content.normalizer import (
    PresentationContentNormalizer,
)
from backend.presentation.content.validator import (
    PresentationContentValidationError,
    PresentationContentValidator,
)
from backend.presentation.enums import SlideType
from backend.presentation.models import (
    PresentationSpec,
)


class PresentationContentGenerator(Protocol):
    def generate(
        self,
        spec: PresentationSpec,
    ) -> GeneratedPresentationContent: ...


class FakePresentationContentGenerator:
    def generate(
        self,
        spec: PresentationSpec,
    ) -> GeneratedPresentationContent:
        slide_02 = spec.get_slide(SlideType.CURRENT_SITUATION)

        needs = slide_02.facts.get(
            "needs",
            [],
        )

        texts = []

        if needs:
            texts.extend(
                [
                    {
                        "shape_name": ("sv_s02_need_1_title"),
                        "text": "Ruido exterior",
                    },
                    {
                        "shape_name": ("sv_s02_need_1_body"),
                        "text": (
                            "El tráfico nocturno "
                            "afecta al descanso "
                            "en el dormitorio."
                        ),
                    },
                ]
            )

        if len(needs) >= 2:
            texts.extend(
                [
                    {
                        "shape_name": ("sv_s02_need_2_title"),
                        "text": ("Pérdida de confort " "térmico"),
                    },
                    {
                        "shape_name": ("sv_s02_need_2_body"),
                        "text": ("La vivienda pierde " "calor durante " "el invierno."),
                    },
                ]
            )

        texts.extend(
            [
                {
                    "shape_name": ("sv_s03_consequence_1_title"),
                    "text": ("El ruido seguirá " "afectando al descanso"),
                },
                {
                    "shape_name": ("sv_s03_consequence_1_body"),
                    "text": (
                        "La molestia continuará "
                        "mientras no se mejore "
                        "el aislamiento."
                    ),
                },
            ]
        )

        return GeneratedPresentationContent.model_validate(
            {
                "texts": texts,
                "semantic_colors": [],
                "slide08": {
                    "before_text": ("Ruido, frío y descanso interrumpido"),
                    "after_text": ("Confort térmico, silencio y tranquilidad"),
                },
            }
        )


class LLMPresentationContentGenerator:
    def __init__(
        self,
        llm_client,
    ) -> None:
        self._llm_client = llm_client

    def generate(
        self,
        spec: PresentationSpec,
    ) -> GeneratedPresentationContent:
        import json

        from backend.presentation.content.constraints import (
            REQUIRED_SEMANTIC_SLOTS,
            REQUIRED_TEXT_SHAPES,
            TEXT_MAX_CHARACTERS,
        )
        from backend.presentation.content.prompts import (
            CONTENT_SYSTEM_PROMPT,
        )

        relevant_slides = [
            slide
            for slide in spec.slides
            if slide.position
            in (
                2,
                3,
                4,
                6,
                7,
                8,
                11,
            )
        ]

        slide_2_fields = [
            {
                "shape_name": shape_name,
                "max_characters": (TEXT_MAX_CHARACTERS[shape_name]),
            }
            for shape_name in REQUIRED_TEXT_SHAPES
            if shape_name.startswith("sv_s02_")
        ]

        slide_3_fields = [
            {
                "shape_name": shape_name,
                "max_characters": (TEXT_MAX_CHARACTERS[shape_name]),
            }
            for shape_name in REQUIRED_TEXT_SHAPES
            if shape_name.startswith("sv_s03_")
        ]

        slide_7_fields = [
            {
                "shape_name": shape_name,
                "max_characters": (TEXT_MAX_CHARACTERS[shape_name]),
            }
            for shape_name in REQUIRED_TEXT_SHAPES
            if shape_name.startswith("sv_s07_")
        ]

        allowed_benefit_categories = get_allowed_benefit_categories(spec)

        context = {
            "proposal_number": (spec.proposal_number),
            "customer_name": (spec.customer_name),
            "slides": [slide.model_dump(mode="json") for slide in relevant_slides],
            "editable_fields": {
                "slide_2": slide_2_fields,
                "slide_3": slide_3_fields,
                "slide_7": slide_7_fields,
            },
            "required_semantic_slots": list(REQUIRED_SEMANTIC_SLOTS),
            "allowed_benefit_categories": sorted(allowed_benefit_categories),
            "structured_text_limits": {
                "slide06_subtitle": (TEXT_MAX_CHARACTERS["sv_s06_subtitle"]),
                "slide06_solution_lines": [
                    TEXT_MAX_CHARACTERS[f"sv_s06_solution_{index}"]
                    for index in range(
                        1,
                        9,
                    )
                ],
                "slide08_before_text": (TEXT_MAX_CHARACTERS["sv_s08_before_text"]),
                "slide08_after_text": (TEXT_MAX_CHARACTERS["sv_s08_after_text"]),
                "slide11_tip_text": (TEXT_MAX_CHARACTERS["sv_s11_tip_text"]),
            },
        }

        user_prompt = (
            "Genera el contenido completo de las "
            "diapositivas dinámicas indicadas.\n"
            "Debes rellenar TODOS los campos "
            "editables exactamente una vez y "
            "asignar color semántico a los cuatro "
            "slots requeridos.\n"
            "Además:\n"
            "- genera slide06 con subtítulo y solución;\n"
            "- genera los cuatro beneficios de slide 7 "
            "en los campos sv_s07_*;\n"
            "- genera exactamente cuatro benefit_icons, "
            "uno para cada beneficio;\n"
            "- genera slide08 con before_text y "
            "after_text;\n"
            "- genera slide11 con tip_text y "
            "tip_icon_key.\n"
            "No generes precios, cálculos financieros "
            "ni prestaciones que no aparezcan en los "
            "datos.\n\n"
            "DATOS DISPONIBLES:\n"
            + json.dumps(
                context,
                ensure_ascii=False,
                indent=2,
            )
        )

        content = self._llm_client.generate_structured(
            system_prompt=(CONTENT_SYSTEM_PROMPT),
            user_prompt=user_prompt,
            response_model=(GeneratedPresentationContent),
        )

        normalizer = PresentationContentNormalizer()

        content = normalizer.normalize(content)

        validator = PresentationContentValidator()

        corrector = PresentationContentCorrector(self._llm_client)

        max_corrections = 2

        for attempt in range(max_corrections + 1):
            try:
                validator.validate(
                    content,
                    allowed_benefit_categories=(allowed_benefit_categories),
                )

                return content

            except PresentationContentValidationError as exc:
                if attempt >= max_corrections:
                    raise

                content = corrector.correct(
                    content,
                    exc,
                )

                content = normalizer.normalize(content)

        raise RuntimeError("Unexpected content validation state")
