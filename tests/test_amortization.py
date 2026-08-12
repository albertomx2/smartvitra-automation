from decimal import Decimal

from backend.presentation.finance.amortization import (
    calculate_amortization,
)


def test_amortization_calculation():
    result = calculate_amortization(
        investment=Decimal("3971.93"),
        annual_savings=Decimal(500),
    )

    assert result.payback_years == (Decimal("3971.93") / Decimal(500))

    assert result.rows[0].accumulated_savings == Decimal(5000)

    assert result.rows[0].net_benefit == Decimal("1028.07")
