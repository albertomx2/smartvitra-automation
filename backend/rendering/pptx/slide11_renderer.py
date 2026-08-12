from decimal import Decimal

from backend.presentation.enums import (
    SlideType,
)
from backend.presentation.finance.amortization import (
    calculate_amortization,
)
from backend.presentation.formatting.money import (
    format_eur,
)
from backend.presentation.models import (
    PresentationSpec,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)


class Slide11Renderer:
    def render(
        self,
        spec: PresentationSpec,
        renderer: PowerPointRenderer,
    ) -> None:
        slide = spec.get_slide(SlideType.FINAL_PRICE)

        total = slide.facts.get("total")

        if total is None:
            return

        investment = Decimal(str(total))

        renderer.set_text_preserving_style(
            "sv_s11_final_price",
            format_eur(investment),
        )

        renderer.set_text_preserving_style(
            "sv_s11_price_label",
            "Precio final cerrado",
        )

        renderer.set_text_preserving_style(
            "sv_s11_price_details",
            ("IVA incluido · Instalación incluida " "· Sin costes adicionales"),
        )

        # Fixture temporal mientras Preweb
        # no proporcione una fuente real
        # para esta hipótesis.
        annual_savings = Decimal(500)

        amortization = calculate_amortization(
            investment=investment,
            annual_savings=(annual_savings),
        )

        for row_index, row in enumerate(
            amortization.rows,
            start=1,
        ):
            renderer.set_table_cell_text(
                "sv_s11_amortization_table",
                row_index,
                0,
                f"{row.years} años",
            )

            renderer.set_table_cell_text(
                "sv_s11_amortization_table",
                row_index,
                1,
                ("~" f"{format_eur(row.annual_savings)}" " / año"),
            )

            renderer.set_table_cell_text(
                "sv_s11_amortization_table",
                row_index,
                2,
                format_eur(row.accumulated_savings),
            )

            renderer.set_table_cell_text(
                "sv_s11_amortization_table",
                row_index,
                3,
                format_eur(row.net_benefit),
            )

        payback = amortization.payback_years.quantize(Decimal("0.1"))

        renderer.set_text_preserving_style(
            "sv_s11_estimation_note",
            (
                "*Simulación de desarrollo con "
                f"un ahorro anual supuesto de "
                f"{format_eur(annual_savings)}. "
                f"Amortización estimada: "
                f"~{payback} años. "
                "Este cálculo se sustituirá por "
                "los datos reales disponibles."
            ),
        )
