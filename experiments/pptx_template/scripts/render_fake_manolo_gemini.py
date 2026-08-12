from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.llm.gemini import (
    GeminiStructuredClient,
)
from backend.presentation.content.generator import (
    LLMPresentationContentGenerator,
)
from backend.rendering.pptx.content_renderer import (
    PresentationContentRenderer,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from scripts.inspect_presentation_spec import (
    spec as base_spec,
)

load_dotenv(dotenv_path=Path(".env"))

# ------------------------------------------------------------------
# 1. Partimos de una PresentationSpec válida para no depender todavía
#    de PDF, Odoo, PrefWeb o los catálogos reales.
# ------------------------------------------------------------------

data = base_spec.model_dump(mode="python")

data["proposal_number"] = "FAKE-MANOLO-001"
data["customer_name"] = "Manolo"


# ------------------------------------------------------------------
# 2. Sustituimos únicamente los hechos del cliente.
#
#    IMPORTANTE:
#    aquí NO redactamos el contenido comercial.
#    Solo describimos hechos que Gemini podrá utilizar.
# ------------------------------------------------------------------

manolo_needs = [
    {
        "code": "summer_heat",
        "description": (
            "El cliente sufre demasiado calor " "en la vivienda durante el verano."
        ),
        "priority": 5,
        "covered": True,
        "source_text": (
            "En invierno se está bien, pero "
            "en verano hace muchísimo calor. "
            "Quiero algo que funcione bien "
            "tanto en invierno como en verano."
        ),
    },
    {
        "code": "acoustic_noise",
        "description": (
            "El ruido exterior molesta mucho " "al cliente y es una prioridad."
        ),
        "priority": 5,
        "covered": True,
        "source_text": (
            "El ruido de fuera me molesta " "muchísimo y para mí es muy importante."
        ),
    },
    {
        "code": "natural_light",
        "description": (
            "El cliente quiere mejorar o preservar " "la entrada de luz natural."
        ),
        "priority": 4,
        "covered": True,
        "source_text": (
            "Ahora entra poca luz y para mí " "la luminosidad es muy importante."
        ),
    },
]


for slide in data["slides"]:
    position = slide["position"]

    if position == 2:
        slide["facts"] = {
            "needs": manolo_needs,
        }

    elif position == 3:
        slide["facts"] = {
            "need_codes": [
                "summer_heat",
                "acoustic_noise",
                "natural_light",
            ]
        }

    elif position == 4:
        slide["facts"] = {
            "primary_need": manolo_needs[0],
        }


fake_spec = type(base_spec).model_validate(data)


# ------------------------------------------------------------------
# 3. Generación real con Gemini.
# ------------------------------------------------------------------

client = GeminiStructuredClient()

generator = LLMPresentationContentGenerator(client)

content = generator.generate(fake_spec)


print()
print("=" * 80)
print("GENERATED CONTENT — MANOLO")
print("=" * 80)

print(content.model_dump_json(indent=2))


# ------------------------------------------------------------------
# 4. QA semántico muy básico para detectar contaminación evidente
#    del cliente anterior.
#
#    "invierno" NO está prohibido porque Manolo sí ha hablado
#    explícitamente de invierno.
# ------------------------------------------------------------------

all_generated_text = " ".join(item.text for item in content.texts).lower()

forbidden_phrases = (
    "tráfico nocturno",
    "ruido de los coches por la noche",
    "dormitorio",
    "pérdida térmica en invierno",
    "el frío se cuela",
    "entrada de frío",
)

contamination = [phrase for phrase in forbidden_phrases if phrase in all_generated_text]

if contamination:
    raise ValueError(
        "Possible contamination from previous "
        "customer detected: " + ", ".join(contamination)
    )


# ------------------------------------------------------------------
# 5. Render directamente sobre nuestra plantilla experimental.
# ------------------------------------------------------------------

template = Path("experiments/pptx_template/" "input/template.pptx")

output = Path("experiments/pptx_template/" "output/fake_manolo_gemini.pptx")

renderer = PowerPointRenderer(template)

PresentationContentRenderer().render(
    content,
    renderer,
)


# ------------------------------------------------------------------
# 6. La slide 4 necesita una foto.
#
#    Seguimos usando la foto fake porque en esta prueba evaluamos
#    texto/layout, no selección real de assets.
# ------------------------------------------------------------------

renderer.replace_picture(
    "sv_s04_problem_photo",
    Path("experiments/pptx_template/" "input/images/problem_test.jpg"),
)

renderer.save(output)


print()
print("=" * 80)
print("FAKE MANOLO PPTX COMPLETED")
print("=" * 80)
print(output)
