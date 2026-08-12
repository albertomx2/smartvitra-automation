from datetime import date
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.google_maps.street_view import (
    GoogleStreetViewFacadeClient,
)
from backend.integrations.llm.gemini import (
    GeminiStructuredClient,
)
from backend.presentation.content.template_v2_generator import (
    LLMTemplateV2ContentGenerator,
    TemplateV2DeterministicData,
)
from backend.presentation.content.template_v2_normalizer import (
    TemplateV2ContentNormalizer,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_content_renderer import (
    TemplateV2ContentRenderer,
)
from backend.rendering.pptx.template_v2_icon_renderer import (
    TemplateV2IconRenderer,
)
from backend.rendering.pptx.template_v2_image_renderer import (
    TemplateV2ImageRenderer,
)

load_dotenv(dotenv_path=Path(".env"))


TEMPLATE = Path("experiments/pptx_template/input/" "template.pptx")

OUTPUT = Path("experiments/pptx_template/output/" "template_v2_gemini_full_case.pptx")

FAKE_IMAGE = Path("experiments/pptx_template/input/" "images/problem_test.jpg")

FACADE_IMAGE = Path("tmp/gemini_v2/" "cover_facade.jpg")


context = {
    "customer": {
        "city": "Getafe",
    },
    "needs": [
        {
            "code": "summer_heat",
            "priority": 5,
            "description": (
                "La vivienda acumula demasiado " "calor durante el verano."
            ),
            "source_text": (
                "Por la tarde el salón se calienta " "muchísimo y cuesta estar cómodo."
            ),
            "covered": True,
        },
        {
            "code": "acoustic_noise",
            "priority": 4,
            "description": ("El ruido procedente de la calle " "afecta al descanso."),
            "source_text": ("Se escucha bastante el tráfico " "desde los dormitorios."),
            "covered": True,
        },
        {
            "code": "light",
            "priority": 3,
            "description": (
                "El cliente quiere conservar " "la máxima entrada de luz natural."
            ),
            "source_text": (
                "No queremos perder luminosidad " "con las ventanas nuevas."
            ),
            "covered": True,
        },
        {
            "code": "aesthetics",
            "priority": 2,
            "description": (
                "El cliente quiere modernizar " "el aspecto de las ventanas."
            ),
            "source_text": (
                "Las actuales se ven antiguas " "y queremos algo más limpio."
            ),
            "covered": True,
        },
    ],
    "proposal": {
        "openings": [
            {
                "opening_id": "V1",
                "room": "Salón",
                "window_type": ("Ventana oscilobatiente " "de dos hojas"),
                "glass_description": ("Vidrio con control solar " "y argón"),
            },
            {
                "opening_id": "V2",
                "room": "Dormitorio principal",
                "window_type": ("Ventana oscilobatiente " "de una hoja"),
                "glass_description": ("Vidrio bajo emisivo " "con argón"),
            },
            {
                "opening_id": "V3",
                "room": "Dormitorio",
                "window_type": ("Ventana oscilobatiente " "de una hoja"),
                "glass_description": ("Vidrio bajo emisivo " "con argón"),
            },
        ],
        "products": [
            {
                "product_code": "UNIK",
                "product_name": "UNIK",
                "benefits": [
                    {
                        "code": "thermal",
                        "title": ("Aislamiento térmico"),
                        "category": "thermal",
                    },
                    {
                        "code": "acoustic",
                        "title": ("Aislamiento acústico"),
                        "category": "acoustic",
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
                        "name": ("Profundidad del marco"),
                        "value": 76,
                        "unit": "mm",
                    },
                    {
                        "code": "thermal_transmittance",
                        "name": ("Transmitancia térmica Uf"),
                        "value": "0.88",
                        "unit": "W/m²K",
                    },
                    {
                        "code": "acoustic_insulation",
                        "name": ("Aislamiento acústico"),
                        "value": "hasta 48",
                        "unit": "dB",
                    },
                ],
            },
        ],
        "services": [
            {
                "name": ("Instalación completa"),
                "description": ("Instalación con remates " "incluidos."),
            },
        ],
    },
}


deterministic = TemplateV2DeterministicData(
    customer_name=("Carlos Moreno Sánchez"),
    address=("Av. de España 42, Getafe"),
    proposal_number=("FAKE-V2-FULL-002"),
    proposal_date=date(
        2026,
        8,
        13,
    ),
    budget_amount=Decimal("6480.00"),
    budget_valid_until=date(
        2026,
        8,
        27,
    ),
    payment_terms=[
        ("50% Al confirmar " "el pedido"),
        ("30% Al fijar fecha " "de inst."),
        ("20% 7 días después " "de la finalización " "de obra"),
    ],
)


street_view_client = GoogleStreetViewFacadeClient()

cover_facade = street_view_client.download_facade(
    address=deterministic.address,
    output_path=FACADE_IMAGE,
)

generator = LLMTemplateV2ContentGenerator(GeminiStructuredClient())

content = generator.generate(
    context=context,
    deterministic=deterministic,
)

content = TemplateV2ContentNormalizer().normalize(content)

renderer = PowerPointRenderer(TEMPLATE)

TemplateV2ContentRenderer().render(
    content,
    renderer,
)

TemplateV2IconRenderer().render(
    content,
    renderer,
)

images = {
    "cover_photo": cover_facade,
    "problem_photo": FAKE_IMAGE,
    "generated_solution": FAKE_IMAGE,
    "project_photo_1": FAKE_IMAGE,
    "project_photo_2": FAKE_IMAGE,
    "project_photo_3": FAKE_IMAGE,
    "generated_result": FAKE_IMAGE,
}

TemplateV2ImageRenderer().render(
    renderer=renderer,
    images=images,
)

renderer.save(OUTPUT)

print()
print("=" * 80)
print("FULL GEMINI V2 PPTX CREATED")
print("=" * 80)
print()
print(
    content.model_dump_json(
        indent=2,
    )
)
print()
print(f"Output: {OUTPUT}")
