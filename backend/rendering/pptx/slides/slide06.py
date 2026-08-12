from backend.commercial.models import (
    CommercialBrief,
)
from backend.presentation.structured.rooms import (
    build_rooms_table,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)


class Slide06Renderer:
    def render_structured(
        self,
        brief: CommercialBrief,
        renderer: PowerPointRenderer,
    ) -> None:
        self._render_rooms_table(
            brief,
            renderer,
        )

    def _render_rooms_table(
        self,
        brief: CommercialBrief,
        renderer: PowerPointRenderer,
    ) -> None:
        table_content = build_rooms_table(brief.openings)

        # La plantilla dispone de exactamente
        # tres filas para estancias.
        for row_index in range(3):
            if row_index < len(table_content.rows):
                row = table_content.rows[row_index]

                label = row.label
                quantity = str(row.quantity)
            else:
                label = ""
                quantity = ""

            renderer.set_table_cell_text(
                "sv_s06_rooms_table",
                row_index,
                0,
                label,
            )

            renderer.set_table_cell_text(
                "sv_s06_rooms_table",
                row_index,
                1,
                quantity,
            )

        renderer.set_table_cell_text(
            "sv_s06_rooms_table",
            3,
            0,
            "TOTAL",
        )

        renderer.set_table_cell_text(
            "sv_s06_rooms_table",
            3,
            1,
            (f"{table_content.total_quantity} " "ventanas"),
        )
