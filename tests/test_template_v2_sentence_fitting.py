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
