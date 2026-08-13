from backend.generation.payment_terms import (
    resolve_payment_terms,
)


def test_known_prefweb_payment_term():
    result = resolve_payment_terms("ANT50ENT30RESTO FIN")

    assert result == [
        "50% Al confirmar el pedido",
        "30% Al fijar fecha de inst.",
        ("20% 7 días después de " "la finalización de obra"),
    ]


def test_payment_term_matching_is_normalized():
    result = resolve_payment_terms("  ant50ent30resto   fin  ")

    assert result == [
        "50% Al confirmar el pedido",
        "30% Al fijar fecha de inst.",
        ("20% 7 días después de " "la finalización de obra"),
    ]


def test_unknown_payment_term_is_preserved():
    result = resolve_payment_terms("CONTADO")

    assert result == ["CONTADO"]


def test_missing_payment_term_uses_safe_fallback():
    result = resolve_payment_terms(None)

    assert result == ["Condiciones de pago según presupuesto"]
