from backend.presentation.content.template_v2_text_fitter import (
    _fit_sentence,
)


def test_sentence_fitter_does_not_end_in_para():
    text = (
        "Alberto, queremos que disfrutes "
        "de un hogar más tranquilo, seguro "
        "y confortable para toda la familia."
    )

    result = _fit_sentence(
        text,
        90,
    )

    assert len(result) <= 90
    assert not result.lower().endswith(" para")
    assert result.endswith(".")


def test_sentence_fitter_preserves_short_text():
    text = "Alberto, disfruta de un hogar " "más tranquilo y confortable."

    result = _fit_sentence(
        text,
        90,
    )

    assert result == text


def test_sentence_fitter_removes_dangling_connector():
    text = (
        "Alberto, queremos crear un hogar "
        "tranquilo, seguro y confortable "
        "con todas las mejoras necesarias "
        "para disfrutarlo durante años."
    )

    result = _fit_sentence(
        text,
        70,
    )

    forbidden = {
        "para",
        "con",
        "de",
        "del",
        "y",
        "que",
    }

    last_word = result.rstrip(".!?").split()[-1].lower()

    assert last_word not in forbidden
    assert len(result) <= 70


def test_sentence_fitter_handles_secondary_benefit_overflow():
    text = (
        "Mejora el aislamiento acústico de la vivienda "
        "y proporciona un ambiente mucho más tranquilo."
    )

    assert len(text) > 75

    result = _fit_sentence(
        text,
        75,
    )

    assert len(result) <= 75
    assert result.endswith((".", "!", "?"))


def test_sentence_fitter_handles_exact_limit():
    text = (
        "Una mejora clara del confort interior "
        "sin comprometer el diseño de la vivienda."
    )

    maximum = len(text)

    result = _fit_sentence(
        text,
        maximum,
    )

    assert result == text
    assert len(result) <= maximum


def test_sentence_fitter_never_leaves_dangling_connector_after_overflow():
    text = (
        "Disfruta de una vivienda más tranquila "
        "y confortable gracias a una solución "
        "diseñada específicamente para"
    )

    result = _fit_sentence(
        text,
        75,
    )

    forbidden = {
        "a",
        "al",
        "con",
        "de",
        "del",
        "e",
        "el",
        "en",
        "la",
        "las",
        "los",
        "o",
        "para",
        "por",
        "que",
        "sin",
        "u",
        "un",
        "una",
        "y",
    }

    last_word = result.rstrip(".!?").split()[-1].lower()

    assert len(result) <= 75
    assert last_word not in forbidden
