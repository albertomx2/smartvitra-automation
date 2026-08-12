from pathlib import Path

BENEFIT_ICON_CATALOG: dict[str, Path] = {
    "thermal": Path("assets/presentation/icons/benefits/thermal.png"),
    "acoustic": Path("assets/presentation/icons/benefits/acoustic.png"),
    "energy": Path("assets/presentation/icons/benefits/energy.png"),
    "solar_control": Path("assets/presentation/icons/benefits/solar_control.png"),
    "daylight": Path("assets/presentation/icons/benefits/daylight.png"),
    "ventilation": Path("assets/presentation/icons/benefits/ventilation.png"),
    "security": Path("assets/presentation/icons/benefits/security.png"),
    "privacy": Path("assets/presentation/icons/benefits/privacy.png"),
    "durability": Path("assets/presentation/icons/benefits/durability.png"),
    "maintenance": Path("assets/presentation/icons/benefits/maintenance.png"),
    "home_value": Path("assets/presentation/icons/benefits/home_value.png"),
    "aesthetics": Path("assets/presentation/icons/benefits/aesthetics.png"),
    "comfort": Path("assets/presentation/icons/benefits/comfort.png"),
    "humidity": Path("assets/presentation/icons/benefits/humidity.png"),
    # Aliases conceptuales.
    # Todavía no necesitamos un PNG exclusivo para ellos.
    "air_tightness": Path("assets/presentation/icons/benefits/ventilation.png"),
    "weather_protection": Path("assets/presentation/icons/benefits/security.png"),
}


def resolve_benefit_icon(
    icon_key: str,
) -> Path:
    try:
        path = BENEFIT_ICON_CATALOG[icon_key]
    except KeyError as exc:
        raise KeyError(f"Unknown benefit icon: {icon_key}") from exc

    if not path.exists():
        raise FileNotFoundError(f"Benefit icon not found: {path}")

    return path
