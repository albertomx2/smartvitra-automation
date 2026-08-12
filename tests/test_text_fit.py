from backend.presentation.content.text_fit import (
    fit_text_to_limit,
)


def test_short_text_is_unchanged():
    text = "Texto corto."

    assert (
        fit_text_to_limit(
            text,
            50,
        )
        == text
    )


def test_long_text_fits_limit():
    result = fit_text_to_limit(
        (
            "El ruido exterior seguirá afectando "
            "al confort de la vivienda durante "
            "mucho tiempo si no se actúa."
        ),
        70,
    )

    assert len(result) <= 70


def test_text_is_not_cut_mid_word():
    result = fit_text_to_limit(
        "Una vivienda mucho más confortable.",
        20,
    )

    assert result.endswith(".")
    assert len(result) <= 20
