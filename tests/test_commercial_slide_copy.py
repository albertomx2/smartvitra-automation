from backend.generation.narration.script.fixed import (
    FIXED_NARRATION_TEXT,
)


def test_slide05_merges_installation_commitments_and_reviews() -> None:
    narration = FIXED_NARRATION_TEXT[5].lower()

    assert "instalación profesional" in narration
    assert "remates terminados" in narration
    assert "zona limpia" in narration
    assert "reseñas" in narration
    assert "clientes valoran" in narration
    assert "pintura" not in narration


def test_slide08_explains_who_the_proposal_is_for() -> None:
    narration = FIXED_NARRATION_TEXT[8].lower()

    assert "resolver el problema" in narration
    assert "comparar soluciones" in narration
    assert "asesoramiento" in narration


def test_slide09_explains_fifteen_day_incentive() -> None:
    narration = FIXED_NARRATION_TEXT[9].lower()

    assert "próximos quince días" in narration
    assert "mejora compatible" in narration


def test_slide10_links_non_cumulative_five_day_incentive_with_contact() -> None:
    narration = FIXED_NARRATION_TEXT[10].lower()

    assert "primeros cinco días" in narration
    assert "no acumulativa" in narration
    assert "certificado energético" in narration
    assert "mejoras anteriores" in narration
    assert "cualquier duda" in narration
    assert "no dudéis en preguntarnos" in narration
    assert "gracias por confiar en smartvitra" in narration
