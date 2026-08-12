from enum import StrEnum


class BenefitIcon(StrEnum):
    ACOUSTIC = "acoustic"
    THERMAL = "thermal"
    SOLAR_CONTROL = "solar_control"
    ENERGY = "energy"
    LIGHT = "light"
    SECURITY = "security"
    VENTILATION = "ventilation"
    COMFORT = "comfort"
    AESTHETICS = "aesthetics"
    DURABILITY = "durability"
    MAINTENANCE = "maintenance"


BENEFIT_ICON_SHAPES = {
    "s07_benefit_1": "sv_s07_benefit_1_icon",
    "s07_benefit_2": "sv_s07_benefit_2_icon",
    "s07_benefit_3": "sv_s07_benefit_3_icon",
    "s07_benefit_4": "sv_s07_benefit_4_icon",
}
