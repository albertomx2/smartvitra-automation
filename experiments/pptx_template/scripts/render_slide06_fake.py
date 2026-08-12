from pathlib import Path

from backend.presentation.content.models import (
    GeneratedPresentationContent,
)
from backend.presentation.content.slide06 import (
    Slide06Content,
    Slide06SolutionContent,
)
from backend.rendering.pptx.content_renderer import (
    PresentationContentRenderer,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)

TEMPLATE = Path("experiments/pptx_template/" "input/template.pptx")

OUTPUT = Path("experiments/pptx_template/" "output/slide06_fake.pptx")


content = GeneratedPresentationContent(
    slide06=Slide06Content(
        subtitle=("Una solución a medida, " "pensada para tu hogar en Madrid."),
        solutions=Slide06SolutionContent(
            lines=[
                ("Ventanas de PVC de alta " "eficiencia."),
                ("Perfil UNIK de 76 mm " "de profundidad."),
                ("Vidrio adaptado a cada " "estancia."),
                ("Control solar en las zonas " "que lo requieren."),
                ("Bajo emisivo para mejorar " "el aislamiento térmico."),
                ("Argón en la configuración " "de vidrio presupuestada."),
                ("Instalación y aislamiento " "perimetral incluidos."),
                ("Remates exteriores " "perimetrales incluidos."),
            ]
        ),
    )
)


renderer = PowerPointRenderer(TEMPLATE)

PresentationContentRenderer().render(
    content,
    renderer,
)


# Tabla fake para comprobar visualmente
# el renderer sin depender todavía de PrefWeb.

table_values = (
    ("Habitación exterior", "1"),
    ("Habitación interior", "1"),
    ("Habitación puerta", "1"),
)

for row_index, (
    room,
    quantity,
) in enumerate(table_values):
    renderer.set_table_cell_text(
        "sv_s06_rooms_table",
        row_index,
        0,
        room,
    )

    renderer.set_table_cell_text(
        "sv_s06_rooms_table",
        row_index,
        1,
        quantity,
    )

renderer.set_table_cell_text(
    "sv_s06_rooms_table",
    3,
    0,
    "TOTAL",
)

renderer.set_table_cell_text(
    "sv_s06_rooms_table",
    3,
    1,
    "3 ventanas",
)

renderer.save(OUTPUT)

print(f"Written: {OUTPUT}")
