from datetime import date
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.llm.gemini import (
    GeminiStructuredClient,
)
from backend.presentation.content.template_v2_generator import (
    LLMTemplateV2ContentGenerator,
    TemplateV2DeterministicData,
)

load_dotenv(dotenv_path=Path(".env"))


context = {
    "customer": {
        "city": "Madrid",
    },
    "needs": [
        {
            "code": "security",
            "priority": 5,
            "description": (
                "El cliente quiere mejorar " "la seguridad de los cerramientos."
            ),
            "source_text": (
                "La vivienda está en una planta baja "
                "y nos preocupa especialmente "
                "la seguridad de las ventanas."
            ),
            "covered": True,
        },
        {
            "code": "privacy",
            "priority": 4,
            "description": (
                "El cliente quiere aumentar " "la privacidad desde el exterior."
            ),
            "source_text": ("Desde la calle se ve demasiado " "el interior del salón."),
            "covered": True,
        },
        {
            "code": "condensation",
            "priority": 4,
            "description": (
                "Aparece condensación en algunas " "ventanas durante el invierno."
            ),
            "source_text": (
                "En invierno aparecen gotas " "en los cristales del dormitorio."
            ),
            "covered": True,
        },
    ],
    "proposal": {
        "openings": [
            {
                "opening_id": "V1",
                "room": "Salón",
                "window_type": "Ventana 2 hojas",
                "glass_description": ("Vidrio laminado de seguridad"),
            },
            {
                "opening_id": "V2",
                "room": "Dormitorio",
                "window_type": "Ventana 2 hojas",
                "glass_description": ("Vidrio bajo emisivo con argón"),
            },
        ],
        "products": [
            {
                "product_code": "UNIK",
                "product_name": "UNIK",
                "benefits": [
                    {
                        "code": "thermal",
                        "title": "Aislamiento térmico",
                        "category": "thermal",
                    },
                    {
                        "code": "security",
                        "title": "Mayor seguridad",
                        "category": "security",
                    },
                ],
                "technical_properties": [
                    {
                        "code": "material",
                        "name": "Material",
                        "value": "PVC",
                    },
                    {
                        "code": "frame_depth",
                        "name": "Profundidad del marco",
                        "value": 76,
                        "unit": "mm",
                    },
                ],
            },
        ],
        "services": [
            {
                "name": "Instalación completa",
                "description": ("Instalación con remates incluidos."),
            },
        ],
    },
}


deterministic = TemplateV2DeterministicData(
    customer_name="Laura Fernández",
    address="C/ Embajadores 118, Madrid",
    proposal_number="FAKE-V2-SEC-001",
    proposal_date=date(
        2026,
        8,
        12,
    ),
    budget_amount=Decimal("5720.00"),
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


generator = LLMTemplateV2ContentGenerator(GeminiStructuredClient())

content = generator.generate(
    context=context,
    deterministic=deterministic,
)

print()
print("=" * 80)
print("GEMINI TEMPLATE V2 CONTENT")
print("=" * 80)
print()

print(
    content.model_dump_json(
        indent=2,
    )
)
