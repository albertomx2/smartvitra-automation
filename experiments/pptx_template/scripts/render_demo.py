from pathlib import Path

from backend.rendering.pptx.models import (
    SemanticColor,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)

INPUT = Path("experiments/pptx_template/input/template.pptx")

OUTPUT = Path("experiments/pptx_template/output/" "rendered_style_preserved.pptx")


renderer = PowerPointRenderer(INPUT)

renderer.set_text_preserving_style(
    "sv_s02_need_1_title",
    "Ruido exterior",
    max_characters=35,
)

renderer.set_text_preserving_style(
    "sv_s02_need_1_body",
    ("El tráfico nocturno afecta " "al descanso en el dormitorio."),
    max_characters=90,
)

renderer.set_text_preserving_style(
    "sv_s02_need_2_title",
    "Pérdida de confort térmico",
    max_characters=35,
)

renderer.set_text_preserving_style(
    "sv_s02_need_2_body",
    ("La vivienda pierde calor " "durante el invierno."),
    max_characters=90,
)

renderer.set_text_preserving_style(
    "sv_s03_consequence_1_title",
    "El ruido seguirá afectando al descanso",
    max_characters=45,
)

renderer.set_text_preserving_style(
    "sv_s03_consequence_1_body",
    ("La molestia continuará mientras " "no se mejore el aislamiento."),
    max_characters=100,
)

renderer.set_shape_border_color(
    "Rectángulo 3",
    SemanticColor.PROBLEM_HIGH,
)

renderer.set_shape_border_color(
    "Rectángulo 4",
    SemanticColor.PROBLEM_HIGH,
)

renderer.set_shape_border_color(
    "Rectángulo 5",
    SemanticColor.POSITIVE,
)

renderer.set_shape_border_color(
    "Rectángulo 6",
    SemanticColor.POSITIVE,
)

renderer.replace_picture(
    "sv_s04_problem_photo",
    Path("experiments/pptx_template/input/" "images/problem_test.jpg"),
)

renderer.save(OUTPUT)

print(f"Written: {OUTPUT}")
