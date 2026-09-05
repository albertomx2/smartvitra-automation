from __future__ import annotations

from pathlib import Path
from typing import Final

from backend.generation.narration.script.models import (
    NarrationSlide,
)

FIXED_NARRATION_VERSION: Final = "v1"
FIXED_NARRATION_VOICE_ID: Final = "SIKGLxQDD9IQ2ip3wCI1"

FIXED_NARRATION_TEXT: Final[dict[int, str]] = {
    4: (
        "Sabemos que el resultado final depende de una instalación impecable. "
        "En SmartVitra nos encargamos de todo: protegemos los suelos y los "
        "muebles cercanos, realizamos una instalación profesional, cuidamos "
        "los remates de albañilería y dejamos todo limpio. Queremos que el "
        "trabajo quede perfecto y sin preocupaciones."
    ),
    5: (
        "Aquí puedes ver algunos de nuestros proyectos ya terminados. Estas "
        "imágenes te ayudarán a visualizar el tipo de resultado que podemos "
        "conseguir también en tu hogar."
    ),
    6: (
        "La mejor prueba de nuestro compromiso es la opinión de otros "
        "clientes. Muchos destacan nuestra profesionalidad, el cuidado, la "
        "limpieza y el cumplimiento de los plazos. Nos esforzamos para que "
        "cada cliente quede realmente satisfecho."
    ),
    8: (
        "Queremos presentarte también una alternativa de buena calidad y "
        "fiable, con una configuración más contenida. Esta opción permite "
        "ajustar la inversión manteniendo un buen nivel de prestaciones. El "
        "presupuesto mostrado no está calculado con esta alternativa."
    ),
    9: (
        "Nuestra recomendación es la opción de mayores prestaciones, que es "
        "la utilizada para calcular el presupuesto. Ambas alternativas son "
        "válidas, pero creemos que esta ofrece el mejor equilibrio entre "
        "confort, calidad y durabilidad. Y si tienes alguna pregunta o "
        "inquietud, no dudes en contactarnos. Estamos aquí para lo que "
        "necesites. ¡Muchas gracias por confiar en SmartVitra! Esperamos "
        "formar parte muy pronto de tu hogar."
    ),
}

FIXED_OBJECTIVES: Final[dict[int, str]] = {
    4: "risk_reduction",
    5: "visual_evidence",
    6: "social_proof",
    8: "value_alternative",
    9: "recommended_solution",
}


def build_fixed_narration_slides() -> dict[int, NarrationSlide]:
    return {
        slide_number: NarrationSlide(
            slide_number=slide_number,
            commercial_objective=FIXED_OBJECTIVES[slide_number],
            estimated_duration_seconds=max(
                5,
                round(len(text.split()) / 135 * 60),
            ),
            narration=text,
        )
        for slide_number, text in FIXED_NARRATION_TEXT.items()
    }


def fixed_audio_path(slide_number: int) -> Path:
    if slide_number not in FIXED_NARRATION_TEXT:
        raise ValueError(f"Slide {slide_number} has no fixed narration")

    project_root = Path(__file__).resolve().parents[4]

    return (
        project_root
        / "assets"
        / "narration"
        / "fixed"
        / FIXED_NARRATION_VERSION
        / f"slide_{slide_number:02d}.mp3"
    )
