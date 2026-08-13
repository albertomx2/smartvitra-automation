from __future__ import annotations

_PAYMENT_TERM_MAPPINGS: dict[
    str,
    list[str],
] = {
    "ANT50ENT30RESTO FIN": [
        "50% Al confirmar el pedido",
        "30% Al fijar fecha de inst.",
        ("20% 7 días después de " "la finalización de obra"),
    ],
}


def resolve_payment_terms(
    payment_term: str | None,
) -> list[str]:
    """
    Convert a PrefWeb payment-term code into the
    customer-facing text used in the proposal.

    Known internal PrefWeb codes are translated
    explicitly. Unknown values are preserved rather
    than replaced by invented payment conditions.
    """

    if payment_term is None:
        return ["Condiciones de pago según presupuesto"]

    cleaned = " ".join(payment_term.strip().split())

    if not cleaned:
        return ["Condiciones de pago según presupuesto"]

    normalized = cleaned.upper()

    mapped = _PAYMENT_TERM_MAPPINGS.get(normalized)

    if mapped is not None:
        return list(mapped)

    # Prefer the real PrefWeb value to inventing
    # commercial conditions that we do not know.
    return [cleaned]
