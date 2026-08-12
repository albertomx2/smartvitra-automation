from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)


class FakeTemplateV2ContentGenerator:
    def generate(
        self,
    ) -> TemplateV2PresentationContent:
        return TemplateV2PresentationContent.model_validate(
            {
                "slide01": {
                    "intro_text": (
                        "Hemos estudiado esta "
                        "vivienda para crear una "
                        "solución orientada al "
                        "confort térmico, el "
                        "aislamiento acústico y "
                        "la funcionalidad."
                    ),
                    "customer_name": ("Manolo García"),
                    "address": ("C/ Alcalá 215, Madrid"),
                    "proposal_number": ("FAKE-00231"),
                    "date": ("12/08/26"),
                },
                "slide02": {
                    "issues": [
                        {
                            "keyword": "CALOR EXCESIVO",
                            "detail": ("durante las tardes " "de verano"),
                        },
                        {
                            "keyword": "RUIDO EXTERIOR",
                            "detail": ("en las zonas " "de descanso"),
                        },
                        {
                            "keyword": "CAJONES DE PERSIANA",
                            "detail": ("con poco aislamiento"),
                        },
                        {
                            "keyword": "VENTANAS ANTIGUAS",
                            "detail": ("con prestaciones " "limitadas"),
                        },
                        {
                            "keyword": "CONFORT REDUCIDO",
                            "detail": ("en las horas de " "más calor"),
                        },
                    ],
                    "impact_statement": ("CALOR INSOPORTABLE"),
                },
                "slide03": {
                    "solutions": [
                        {
                            "text": ("PVC de altas " "prestaciones"),
                            "icon_key": ("durability"),
                        },
                        {
                            "text": ("Vidrio con " "control solar"),
                            "icon_key": ("solar_control"),
                        },
                        {
                            "text": ("Aislamiento " "acústico reforzado"),
                            "icon_key": ("acoustic"),
                        },
                        {
                            "text": ("Microventilación"),
                            "icon_key": ("ventilation"),
                        },
                    ],
                    "main_benefit": (
                        "Una vivienda más " "confortable durante " "todo el año."
                    ),
                    "secondary_benefit": (
                        "Menos ruido y mejor " "protección frente al " "calor exterior."
                    ),
                    "benefit_claim": ("CONFORT, SILENCIO, " "EFICIENCIA Y CALIDAD"),
                },
                "slide07": {
                    "project_summary": [
                        ("3 ventanas de PVC " "UNIK"),
                        ("Vidrio con control " "solar en salón"),
                        ("Cajones " "thermoacústicos en " "dos estancias"),
                        ("Instalación y " "remates incluidos"),
                    ],
                    "budget_amount": ("4.180€"),
                    "budget_valid_until": ("26/08/26"),
                    "payment_terms": [
                        ("50% Al confirmar " "el pedido"),
                        ("30% Al fijar fecha " "de inst."),
                        ("20% 7 días después " "de la finalización " "de obra"),
                    ],
                },
            }
        )
