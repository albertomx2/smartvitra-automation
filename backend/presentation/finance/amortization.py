from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class AmortizationRow:
    years: int
    annual_savings: Decimal
    accumulated_savings: Decimal
    net_benefit: Decimal


@dataclass(frozen=True)
class AmortizationResult:
    annual_savings: Decimal
    payback_years: Decimal
    rows: tuple[AmortizationRow, ...]


def calculate_amortization(
    *,
    investment: Decimal,
    annual_savings: Decimal,
    periods: tuple[int, ...] = (
        10,
        15,
        20,
        30,
    ),
) -> AmortizationResult:
    if investment <= 0:
        raise ValueError("investment must be positive")

    if annual_savings <= 0:
        raise ValueError("annual_savings must be positive")

    rows = []

    for years in periods:
        accumulated = annual_savings * Decimal(years)

        rows.append(
            AmortizationRow(
                years=years,
                annual_savings=annual_savings,
                accumulated_savings=(accumulated),
                net_benefit=(accumulated - investment),
            )
        )

    return AmortizationResult(
        annual_savings=annual_savings,
        payback_years=(investment / annual_savings),
        rows=tuple(rows),
    )
