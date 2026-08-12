from datetime import date
from decimal import Decimal

from backend.presentation.content.template_v2_generator import (
    LLMTemplateV2ContentGenerator,
    TemplateV2DeterministicData,
)
from backend.presentation.content.template_v2_llm_models import (
    TemplateV2LLMContent,
)


class FakeLLMClient:
    def generate_structured(
        self,
        *,
        system_prompt,
        user_prompt,
        response_model,
    ):
        assert response_model is TemplateV2LLMContent

        return TemplateV2LLMContent.model_validate(
            {
                "slide01": {
                    "intro_text": ("Texto personalizado."),
                },
                "slide02": {
                    "issues": [
                        {
                            "keyword": "CALOR EXCESIVO",
                            "detail": "por las tardes",
                        },
                        {
                            "keyword": "ALTA TEMPERATURA",
                            "detail": "en verano",
                        },
                        {
                            "keyword": "MENOR CONFORT",
                            "detail": "en las horas de sol",
                        },
                        {
                            "keyword": "RUIDO EXTERIOR",
                            "detail": "en el dormitorio",
                        },
                        {
                            "keyword": "DESCANSO LIMITADO",
                            "detail": "por el tráfico",
                        },
                    ],
                    "impact_statement": ("CALOR INSOPORTABLE"),
                },
                "slide03": {
                    "solutions": [
                        {
                            "text": ("Vidrio con control solar"),
                            "icon_key": ("solar_control"),
                        }
                    ],
                    "main_benefit": ("Más confort en verano."),
                    "secondary_benefit": ("Mayor tranquilidad."),
                    "benefit_claim": ("CONFORT Y TRANQUILIDAD"),
                },
                "slide07": {
                    "project_summary": [
                        "3 ventanas de PVC",
                    ]
                },
            }
        )


def test_deterministic_data_are_not_llm_generated():
    generator = LLMTemplateV2ContentGenerator(FakeLLMClient())

    deterministic = TemplateV2DeterministicData(
        customer_name="Alberto",
        address="Calle Test 1",
        proposal_number="S00999",
        proposal_date=date(
            2026,
            8,
            12,
        ),
        budget_amount=Decimal("4180.00"),
        budget_valid_until=date(
            2026,
            8,
            26,
        ),
        payment_terms=[
            "50% Al confirmar el pedido",
            "30% Al fijar fecha de inst.",
            ("20% 7 días después de " "la finalización de obra"),
        ],
    )

    content = generator.generate(
        context={
            "needs": [
                "summer_heat",
            ]
        },
        deterministic=deterministic,
    )

    assert content.slide01.customer_name == "Alberto"

    assert content.slide01.proposal_number == "S00999"

    assert content.slide07.budget_amount == "4.180€"

    assert content.slide07.budget_valid_until == "26/08/26"
