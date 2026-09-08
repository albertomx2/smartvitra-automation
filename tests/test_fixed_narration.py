from types import SimpleNamespace

from backend.generation.narration.script.fixed import (
    FIXED_NARRATION_TEXT,
)
from backend.generation.narration.script.generator import (
    NarrationScriptGenerator,
)
from backend.generation.narration.script.models import (
    NarrationSlide,
    VariableNarrationScript,
)


def _variable_text(label: str) -> str:
    return " ".join([label] * 35) + "."


def test_generator_requests_only_variable_slides_and_inserts_fixed_copy() -> None:
    class FakeLLM:
        response_model = None
        user_prompt = ""

        def generate_structured(
            self,
            *,
            system_prompt: str,
            user_prompt: str,
            response_model,
        ):
            self.response_model = response_model
            self.user_prompt = user_prompt

            return VariableNarrationScript(
                slides=[
                    NarrationSlide(
                        slide_number=number,
                        commercial_objective=objective,
                        estimated_duration_seconds=15,
                        narration=(
                            "Hola desde C/ Pablo Vidal. "
                            + _variable_text(f"slide{number}")
                            if number == 1
                            else _variable_text(f"slide{number}")
                        ),
                    )
                    for number, objective in [
                        (1, "personalized_opening"),
                        (2, "problem_awareness"),
                        (3, "solution_transformation"),
                    ]
                ]
            )

    llm = FakeLLM()

    script = NarrationScriptGenerator(llm).generate(
        context={
            "customer": {
                "name": "Antonio Manzaneque Conde",
                "address": "C/ Pablo Vidal 7",
            },
            "proposal": {
                "openings": [
                    {
                        "room": "Habitación principal",
                        "quantity": 1,
                        "commercial_notes": None,
                        "window_type": "Corredera Islide 2 hojas",
                        "reference": "IS2200 V",
                        "color": "CE BRONCE",
                        "dimensions": "L=1.400;A=1.165",
                    }
                ]
            },
            "pricing": {
                "discount_applied": True,
                "discount_condition_days": 15,
                "discount_percentage": 15,
                "total": 4478.19,
            },
        },
        presentation_content=SimpleNamespace(
            model_dump=lambda **kwargs: {
                "slide01": {
                    "address": "Calle Pablo Vidal 7",
                },
                "slide02": {},
                "slide03": {
                    "solutions": [
                        {
                            "text": "Modelo IS2200 V",
                        }
                    ],
                    "main_benefit": "Más confort",
                },
                "slide07": {
                    "project_summary": [
                        "Ventana corredera Islide IS2200 V",
                    ]
                },
            },
            slide07=SimpleNamespace(
                payment_terms=[
                    "50% al confirmar el pedido",
                    "50% al finalizar",
                ]
            ),
        ),
    )

    assert llm.response_model is VariableNarrationScript
    assert [slide.slide_number for slide in script.slides] == list(range(1, 10))

    for slide_number, expected_text in FIXED_NARRATION_TEXT.items():
        assert script.slides[slide_number - 1].narration == expected_text

    assert '"discount_applied": true' in llm.user_prompt
    assert "Calle Pablo Vidal 7" in llm.user_prompt
    assert "C/ Pablo Vidal 7" not in llm.user_prompt
    assert "IS2200" not in llm.user_prompt
    assert "Islide" not in llm.user_prompt
    assert "CE BRONCE" not in llm.user_prompt
    assert "Calle Pablo Vidal" in script.slides[0].narration
    assert "C/ Pablo Vidal" not in script.slides[0].narration
    assert "próximos 15 días" in script.slides[6].narration
    assert "15 por ciento" in script.slides[6].narration
    assert "4.478,19 euros" in script.slides[6].narration
    assert "modelo" not in script.slides[6].narration.lower()
    assert "elección de ventanas" in script.slides[6].narration
