from backend.presentation.content.slide06 import (
    Slide06Content,
    Slide06SolutionContent,
)


def test_slide06_content_model():
    content = Slide06Content(
        subtitle=("Una solución pensada para tu vivienda."),
        solutions=Slide06SolutionContent(
            lines=[
                "Ventanas de alta eficiencia.",
                "Vidrio adaptado a la estancia.",
            ]
        ),
    )

    assert content.subtitle == "Una solución pensada para tu vivienda."

    assert len(content.solutions.lines) == 2


def test_generated_content_can_include_slide06():
    from backend.presentation.content.models import (
        GeneratedPresentationContent,
    )

    content = GeneratedPresentationContent(
        slide06=Slide06Content(
            subtitle="Propuesta personalizada.",
            solutions=Slide06SolutionContent(
                lines=[
                    "Solución 1",
                    "Solución 2",
                ]
            ),
        )
    )

    assert content.slide06 is not None

    assert content.slide06.subtitle == "Propuesta personalizada."


def test_slide06_content_can_be_rendered():
    from pathlib import Path

    from backend.presentation.content.models import (
        GeneratedPresentationContent,
    )
    from backend.rendering.pptx.content_renderer import (
        PresentationContentRenderer,
    )
    from backend.rendering.pptx.renderer import (
        PowerPointRenderer,
    )

    template = Path("experiments/pptx_template/" "input/template2.pptx")

    renderer = PowerPointRenderer(template)

    content = GeneratedPresentationContent(
        slide06=Slide06Content(
            subtitle=("Una solución pensada " "para tu vivienda."),
            solutions=Slide06SolutionContent(
                lines=[
                    "Ventanas de PVC.",
                    "Vidrio con control solar.",
                    "Aislamiento acústico.",
                ]
            ),
        )
    )

    PresentationContentRenderer().render(
        content,
        renderer,
    )

    assert (
        renderer.find_shape("sv_s06_subtitle").text
        == "Una solución pensada para tu vivienda."
    )

    assert renderer.find_shape("sv_s06_solution_1").text == "Ventanas de PVC."

    assert renderer.find_shape("sv_s06_solution_2").text == "Vidrio con control solar."

    assert renderer.find_shape("sv_s06_solution_3").text == "Aislamiento acústico."

    assert renderer.find_shape("sv_s06_solution_8").text == ""
