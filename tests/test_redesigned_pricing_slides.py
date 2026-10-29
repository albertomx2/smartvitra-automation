from pathlib import Path

from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_content_renderer import (
    TemplateV2ContentRenderer,
)

TEMPLATE = Path("experiments/pptx_template/input/template.pptx")


def test_pricing_slides_calculate_both_material_alternatives() -> None:
    content = TemplateV2PresentationContent.model_validate(
        {
            "slide01": {
                "intro_text": "Propuesta personalizada.",
                "customer_name": "Cliente",
                "address": "Calle Ejemplo 1",
                "proposal_number": "S00100",
                "date": "28/10/26",
            },
            "slide02": {
                "issues": [
                    {
                        "keyword": "RUIDO",
                        "detail": "procedente del exterior",
                    }
                ],
                "impact_statement": "MENOR CONFORT",
            },
            "slide03": {
                "solutions": [
                    {
                        "text": "Mejora del aislamiento",
                        "icon_key": "thermal_insulation",
                    }
                ],
                "main_benefit": "Más confort interior.",
                "secondary_benefit": "Menos ruido exterior.",
                "benefit_claim": "CONFORT Y AISLAMIENTO",
            },
            "slide07": {
                "project_summary": ["Una ventana"],
                "budget_amount": "10.164€",
                "budget_valid_until": "Consultar",
                "payment_terms": [],
            },
        }
    )
    renderer = PowerPointRenderer(TEMPLATE)

    TemplateV2ContentRenderer().render(content, renderer)

    assert len(renderer.presentation.slides) == 10
    assert renderer.find_shape("sv_s07_budget_amount").text == "10.164 €"
    assert renderer.find_shape("sv_s07_thermofibra_reference_left").text == "10.164 €"
    assert renderer.find_shape("sv_s07_thermofibra_reference_right").text == "10.164 €"
    assert renderer.find_shape("sv_s07_cortizo_amount").text == "8.639 €"
    assert renderer.find_shape("sv_s07_refine_amount").text == "11.180 €"
