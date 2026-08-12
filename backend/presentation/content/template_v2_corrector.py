import json

from backend.integrations.llm.models import (
    StructuredLLMClient,
)
from backend.presentation.content.template_v2_constraints import (
    TEMPLATE_V2_TEXT_LIMITS,
)
from backend.presentation.content.template_v2_llm_models import (
    TemplateV2LLMContent,
)
from backend.presentation.content.template_v2_validator import (
    TemplateV2ValidationError,
)

TEMPLATE_V2_CORRECTION_PROMPT = """
Eres el corrector de contenido comercial
de SmartVitra.

Recibirás contenido previamente generado
y errores exactos de validación.

Corrige exclusivamente los errores
indicados.

REGLAS:

1. No cortes frases.
2. No termines textos con artículos,
   preposiciones o fragmentos incompletos.
3. Reescribe de forma natural para caber
   dentro del límite.
4. Conserva el significado original.
5. No inventes características ni problemas.
6. Conserva exactamente cinco issues.
7. Conserva el orden y estructura JSON.
8. Conserva los icon_key salvo que sean
   incoherentes con la solución.
9. Los textos comerciales deben ser frases
   completas aunque sean muy breves.
10. Si un error indica un campo sv_s02_issue_N,
    corrige exactamente el elemento N de
    slide02.issues.
11. Para slide02, el límite se aplica a la
    concatenación de keyword + espacio + detail.
12. Debes reducir realmente la longitud hasta
    cumplir el máximo indicado.
13. Devuelve únicamente la estructura JSON.
"""


class TemplateV2ContentCorrector:
    def __init__(
        self,
        llm_client: StructuredLLMClient,
    ) -> None:
        self._llm_client = llm_client

    def correct(
        self,
        *,
        llm_content: TemplateV2LLMContent,
        error: TemplateV2ValidationError,
    ) -> TemplateV2LLMContent:
        violations = [
            {
                "field": violation.field,
                "reason": violation.reason,
            }
            for violation in (error.violations)
        ]

        payload = {
            "validation_errors": violations,
            "text_limits": TEMPLATE_V2_TEXT_LIMITS,
            "field_mapping": {
                "sv_s02_issue_1": "slide02.issues[0]",
                "sv_s02_issue_2": "slide02.issues[1]",
                "sv_s02_issue_3": "slide02.issues[2]",
                "sv_s02_issue_4": "slide02.issues[3]",
                "sv_s02_issue_5": "slide02.issues[4]",
                "sv_s02_issue_6": "slide02.impact_statement",
                "sv_s03_solution_1": "slide03.solutions[0].text",
                "sv_s03_solution_2": "slide03.solutions[1].text",
                "sv_s03_solution_3": "slide03.solutions[2].text",
                "sv_s03_solution_4": "slide03.solutions[3].text",
                "sv_s03_solution_5": "slide03.solutions[4].text",
                "sv_s03_solution_6": "slide03.solutions[5].text",
                "sv_s03_main_benefit": "slide03.main_benefit",
                "sv_s03_main_benefit_secondary": ("slide03.secondary_benefit"),
                "sv_s03_benefit_claim": "slide03.benefit_claim",
            },
            "current_content": (llm_content.model_dump(mode="json")),
        }

        return self._llm_client.generate_structured(
            system_prompt=(TEMPLATE_V2_CORRECTION_PROMPT),
            user_prompt=(
                "Corrige el contenido "
                "según los errores "
                "indicados:\n\n"
                + json.dumps(
                    payload,
                    ensure_ascii=False,
                    indent=2,
                )
            ),
            response_model=(TemplateV2LLMContent),
        )
