from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)

SLIDE03_SOLUTION_COUNT = 6


class TemplateV2LayoutRenderer:
    def render_slide03_solutions(
        self,
        *,
        renderer: PowerPointRenderer,
        active_count: int,
    ) -> None:
        if not 1 <= active_count <= SLIDE03_SOLUTION_COUNT:
            raise ValueError("active_count must be between 1 and 6")

        text_shapes = [
            renderer.find_shape(f"sv_s03_solution_{index}")
            for index in range(
                1,
                SLIDE03_SOLUTION_COUNT + 1,
            )
        ]

        icon_shapes = [
            renderer.find_shape(f"sv_s03_solution_{index}_icon")
            for index in range(
                1,
                SLIDE03_SOLUTION_COUNT + 1,
            )
        ]

        first_text_top = text_shapes[0].top
        last_text_top = text_shapes[-1].top

        first_icon_top = icon_shapes[0].top
        last_icon_top = icon_shapes[-1].top

        if active_count == 1:
            text_tops = [(first_text_top + last_text_top) // 2]

            icon_tops = [(first_icon_top + last_icon_top) // 2]

        else:
            text_step = (last_text_top - first_text_top) / (active_count - 1)

            icon_step = (last_icon_top - first_icon_top) / (active_count - 1)

            text_tops = [
                round(first_text_top + text_step * index)
                for index in range(active_count)
            ]

            icon_tops = [
                round(first_icon_top + icon_step * index)
                for index in range(active_count)
            ]

        for index in range(active_count):
            text_shapes[index].top = text_tops[index]

            icon_shapes[index].top = icon_tops[index]
