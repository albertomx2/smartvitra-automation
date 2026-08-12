from decimal import Decimal

from backend.presentation.formatting.money import (
    format_eur,
)


def test_format_eur_without_decimals():
    assert format_eur(Decimal("4403.48")) == "4.403€"


def test_format_eur_with_decimals():
    assert (
        format_eur(
            Decimal("3282.58"),
            decimals=True,
        )
        == "3.282,58€"
    )
