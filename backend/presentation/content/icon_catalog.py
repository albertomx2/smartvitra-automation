from pathlib import Path

ICON_ROOT = Path("assets/presentation/icons/benefits")


BENEFIT_ICON_KEYS = (
    "thermal",
    "acoustic",
    "energy",
    "solar_control",
    "daylight",
    "ventilation",
    "air_tightness",
    "security",
    "privacy",
    "durability",
    "maintenance",
    "home_value",
    "aesthetics",
    "comfort",
    "humidity",
    "weather_protection",
)


BENEFIT_ICON_FILES = {key: ICON_ROOT / f"{key}.png" for key in BENEFIT_ICON_KEYS}


def get_benefit_icon_path(
    icon_key: str,
) -> Path:
    try:
        path = BENEFIT_ICON_FILES[icon_key]
    except KeyError as exc:
        raise ValueError("Unknown benefit icon key: " f"{icon_key}") from exc

    if not path.exists():
        raise FileNotFoundError(path)

    return path
