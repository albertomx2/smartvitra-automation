from backend.generation.narration.script.fitter import (
    NarrationScriptFitter,
)
from backend.generation.narration.script.fixed import (
    FIXED_NARRATION_TEXT,
    build_fixed_narration_slides,
)
from backend.generation.narration.script.models import (
    NarrationScript,
    NarrationSlide,
)


def test_narration_text_fitter_preserves_short_text():
    text = "Esta es una narración breve y completa " "que no necesita ningún ajuste."

    result = NarrationScriptFitter._fit_text(
        text,
        50,
    )

    assert result == text


def test_narration_text_fitter_never_exceeds_word_limit():
    text = " ".join(f"palabra{i}" for i in range(100))

    result = NarrationScriptFitter._fit_text(
        text,
        40,
    )

    assert len(result.split()) <= 40


def test_narration_text_fitter_does_not_cut_words():
    text = (
        "Queremos mejorar el confort de la vivienda "
        "mediante una instalación cuidada y profesional "
        "que permita disfrutar de mejores prestaciones."
    )

    result = NarrationScriptFitter._fit_text(
        text,
        13,
    )

    assert len(result.split()) <= 13
    assert result.endswith((".", "!", "?"))


def test_narration_text_fitter_removes_dangling_connector():
    text = (
        "La propuesta busca mejorar claramente el confort "
        "interior de la vivienda y proporcionar una solución "
        "adecuada para"
    )

    result = NarrationScriptFitter._fit_text(
        text,
        16,
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

    assert last_word not in forbidden


def test_narration_fitter_never_changes_fixed_slides():
    fixed = build_fixed_narration_slides()
    variable_text = " ".join(["contenido"] * 100)

    slides = []

    for number in range(1, 10):
        slides.append(
            fixed.get(number)
            or NarrationSlide(
                slide_number=number,
                commercial_objective="variable",
                estimated_duration_seconds=30,
                narration=variable_text,
            )
        )

    result = NarrationScriptFitter().fit(
        NarrationScript(
            estimated_duration_seconds=200,
            word_count=500,
            slides=slides,
        )
    )

    for slide_number, expected_text in FIXED_NARRATION_TEXT.items():
        assert result.slides[slide_number - 1].narration == expected_text

    assert len(result.full_text.split()) <= NarrationScriptFitter.TARGET_MAX_WORDS
