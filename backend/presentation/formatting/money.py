from decimal import Decimal


def format_eur(
    value: Decimal,
    *,
    decimals: bool = False,
) -> str:
    if decimals:
        formatted = f"{value:,.2f}"
    else:
        formatted = f"{value:,.0f}"

    formatted = formatted.replace(",", "_").replace(".", ",").replace("_", ".")

    return f"{formatted}€"
