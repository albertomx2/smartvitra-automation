from decimal import Decimal

from backend.integrations.pdf.utils import parse_euro_decimal


def test_parse_standard_euro_decimal():
    assert parse_euro_decimal("4.403,48") == Decimal("4403.48")


def test_parse_simple_euro_decimal():
    assert parse_euro_decimal("689,35") == Decimal("689.35")


def test_parse_negative_euro_decimal():
    assert parse_euro_decimal("-101,52") == Decimal("-101.52")


def test_parse_negative_euro_decimal_with_hidden_unicode():
    assert parse_euro_decimal("-\u200b101,52") == Decimal("-101.52")
