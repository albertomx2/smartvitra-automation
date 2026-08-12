from backend.needs.models import (
    CustomerNeedCode,
    CustomerNeedDefinition,
)

NEED_DEFINITIONS: dict[
    CustomerNeedCode,
    CustomerNeedDefinition,
] = {
    CustomerNeedCode.ACOUSTIC_NOISE: CustomerNeedDefinition(
        code=CustomerNeedCode.ACOUSTIC_NOISE,
        name="Ruido exterior",
        description=("El cliente quiere reducir el ruido " "procedente del exterior."),
        benefit_categories=[
            "acoustic",
        ],
    ),
    CustomerNeedCode.THERMAL_LOSS: CustomerNeedDefinition(
        code=CustomerNeedCode.THERMAL_LOSS,
        name="Pérdida térmica",
        description=(
            "El cliente quiere mejorar el " "aislamiento térmico de la vivienda."
        ),
        benefit_categories=[
            "thermal",
        ],
    ),
    CustomerNeedCode.SUMMER_HEAT: CustomerNeedDefinition(
        code=CustomerNeedCode.SUMMER_HEAT,
        name="Exceso de calor en verano",
        description=(
            "El cliente quiere reducir el "
            "sobrecalentamiento de la vivienda "
            "durante los meses cálidos."
        ),
        benefit_categories=[
            "solar_control",
            "thermal",
        ],
    ),
    CustomerNeedCode.CONDENSATION: CustomerNeedDefinition(
        code=CustomerNeedCode.CONDENSATION,
        name="Condensación",
        description=("El cliente presenta problemas " "relacionados con condensación."),
        benefit_categories=[
            "ventilation",
            "thermal",
        ],
    ),
    CustomerNeedCode.VENTILATION: CustomerNeedDefinition(
        code=CustomerNeedCode.VENTILATION,
        name="Ventilación",
        description=("El cliente quiere mejorar la " "ventilación controlada."),
        benefit_categories=[
            "ventilation",
        ],
    ),
    CustomerNeedCode.SECURITY: CustomerNeedDefinition(
        code=CustomerNeedCode.SECURITY,
        name="Seguridad",
        description=("El cliente quiere mejorar la " "seguridad de los cerramientos."),
        benefit_categories=[
            "security",
        ],
    ),
    CustomerNeedCode.PRIVACY: CustomerNeedDefinition(
        code=CustomerNeedCode.PRIVACY,
        name="Privacidad",
        description=("El cliente quiere aumentar la " "privacidad."),
        benefit_categories=[
            "privacy",
        ],
    ),
    CustomerNeedCode.LIGHT: CustomerNeedDefinition(
        code=CustomerNeedCode.LIGHT,
        name="Luminosidad",
        description=("El cliente quiere mejorar la " "entrada de luz natural."),
        benefit_categories=[
            "daylight",
        ],
    ),
    CustomerNeedCode.AESTHETICS: CustomerNeedDefinition(
        code=CustomerNeedCode.AESTHETICS,
        name="Estética",
        description=(
            "El cliente quiere mejorar el " "aspecto visual de los cerramientos."
        ),
        benefit_categories=[
            "aesthetics",
        ],
    ),
}
