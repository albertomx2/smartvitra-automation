import json

from backend.integrations.llm.models import (
    StructuredLLMClient,
)
from backend.presentation.content.constraints import (
    TEXT_MAX_CHARACTERS,
)
from backend.presentation.content.models import (
    GeneratedPresentationContent,
)
from backend.presentation.content.validator import (
    PresentationContentValidationError,
)

CORRECTION_SYSTEM_PROMPT = """
Eres el componente de corrección de contenido
de SmartVitra.

Recibirás una generación comercial completa y una
lista exacta de errores detectados por el validador.

Tu tarea es devolver de nuevo TODO el objeto
GeneratedPresentationContent corregido.

REGLAS GENERALES

1. Corrige únicamente los errores indicados.
2. Conserva todos los datos correctos existentes.
3. No inventes problemas, productos, prestaciones,
   precios, cifras ni características técnicas.
4. No elimines campos obligatorios.
5. No añadas campos desconocidos.
6. Mantén la personalización del cliente.
7. Devuelve únicamente la estructura solicitada.

TEXTS

8. Mantén exactamente los shape_name requeridos.
9. Si un texto supera su límite, reescríbelo de forma
   natural dentro del máximo permitido.
10. No cortes palabras ni frases abruptamente.

SEMANTIC COLORS

11. Mantén exactamente los cuatro slots requeridos.
12. Cada slot debe aparecer una sola vez.

SLIDE06

13. Si slide06 falta o es inválida, genérala usando
    únicamente productos, vidrios, servicios y datos
    técnicos ya presentes en el contenido recibido.
14. No introduzcas soluciones inexistentes.

BENEFIT ICONS

15. Deben existir exactamente los índices 1, 2, 3 y 4.
16. No dupliques índices.
17. category e icon_key deben coincidir.
18. El concepto debe corresponder al beneficio de la
    misma posición.

SLIDE08

19. Debe conservar before_text y after_text.
20. Ambos deben respetar sus límites y reflejar
    únicamente problemas y mejoras respaldados por
    los datos.

SLIDE11

21. tip_text debe respetar su límite.
22. No inventes vida útil, garantías, porcentajes,
    ahorros ni otras cifras.
23. tip_icon_key debe ser compatible con el schema.
"""


class PresentationContentCorrector:
    def __init__(
        self,
        llm_client: StructuredLLMClient,
    ) -> None:
        self._llm_client = llm_client

    def correct(
        self,
        content: GeneratedPresentationContent,
        error: PresentationContentValidationError,
    ) -> GeneratedPresentationContent:
        violations = [
            {
                "field": violation.field,
                "reason": violation.reason,
            }
            for violation in error.violations
        ]

        payload = {
            "validation_errors": violations,
            "text_limits": (TEXT_MAX_CHARACTERS),
            "current_content": (content.model_dump(mode="json")),
        }

        return self._llm_client.generate_structured(
            system_prompt=(CORRECTION_SYSTEM_PROMPT),
            user_prompt=(
                "Corrige el contenido "
                "siguiendo exactamente "
                "los errores indicados.\n\n"
                + json.dumps(
                    payload,
                    ensure_ascii=False,
                    indent=2,
                )
            ),
            response_model=(GeneratedPresentationContent),
        )
