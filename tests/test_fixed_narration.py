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
                        narration=_variable_text(f"slide{number}"),
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
            "pricing": {
                "discount_applied": True,
                "discount_condition_days": 15,
                "discount_percentage": 15,
                "total": 4478.19,
            }
        },
        presentation_content=SimpleNamespace(
            model_dump=lambda **kwargs: {},
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
    assert "próximos 15 días" in script.slides[6].narration
    assert "15 por ciento" in script.slides[6].narration
    assert "4.478,19 euros" in script.slides[6].narration
    assert "modelo" not in script.slides[6].narration.lower()
    assert "elección de ventanas" in script.slides[6].narration
