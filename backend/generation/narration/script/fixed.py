from __future__ import annotations

from pathlib import Path
from typing import Final

from backend.generation.narration.script.models import (
    NarrationSlide,
)

FIXED_NARRATION_VERSION: Final = "v7"
FIXED_NARRATION_VOICE_ID: Final = "SIKGLxQDD9IQ2ip3wCI1"

FIXED_NARRATION_TEXT: Final[dict[int, str]] = {
    4: (
        "Aquí podéis ver algunos proyectos de SmartVitra ya terminados. Estas "
        "imágenes ayudan a visualizar el cuidado de los acabados y el tipo de "
        "resultado que podemos conseguir también en vuestra vivienda."
    ),
    5: (
        "En SmartVitra protegemos la vivienda, realizamos una instalación "
        "profesional y dejamos los remates terminados y la zona limpia. Además, "
        "podéis comprobar en algunas reseñas cómo nuestros clientes valoran el "
        "cuidado, la limpieza y el resultado final."
    ),
    8: (
        "Esta propuesta está pensada para quienes quieren resolver el problema "
        "de su vivienda, comparar soluciones y niveles de inversión, y valoran "
        "el asesoramiento y una instalación cuidada. Si solo importa la cifra "
        "final, sin comparar qué incluye, probablemente no seamos la opción "
        "adecuada. Ofrecemos tres líneas de producto y una recomendación "
        "adaptada a cada vivienda y presupuesto."
    ),
    9: (
        "Si aceptáis la propuesta dentro de los próximos quince días, "
        "acordaremos una mejora compatible con la solución elegida. Puede ser "
        "la motorización de una persiana, una mosquitera, el forrado de una "
        "peana o una mejora del acristalamiento. La opción aplicable quedará "
        "recogida en el documento de aceptación."
    ),
    10: (
        "Si confirmáis durante los primeros cinco días, podréis elegir, de "
        "forma no acumulativa, entre el certificado energético de vuestra "
        "vivienda o una de las mejoras anteriores. Antes de decidir queremos "
        "que todo quede claro. Así que, si tenéis cualquier duda, no dudéis en "
        "preguntarnos. Muchas gracias por confiar en SmartVitra."
    ),
}

FIXED_OBJECTIVES: Final[dict[int, str]] = {
    4: "visual_evidence",
    5: "risk_reduction_and_social_proof",
    8: "audience_fit",
    9: "early_commitment_incentive",
    10: "early_commitment_and_contact",
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
