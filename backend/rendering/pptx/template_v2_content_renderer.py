from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_layout import (
    TemplateV2LayoutRenderer,
)


class TemplateV2ContentRenderer:
    def render(
        self,
        content: TemplateV2PresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        self._render_slide01(
            content,
            renderer,
        )

        self._render_slide02(
            content,
            renderer,
        )

        self._render_slide03(
            content,
            renderer,
        )

        self._render_slide07(
            content,
            renderer,
        )

    def _render_slide01(
        self,
        content: TemplateV2PresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        values = {
            "sv_s01_intro_text": (content.slide01.intro_text),
            "sv_s01_customer_name": (content.slide01.customer_name),
            "sv_s01_address": (content.slide01.address),
            "sv_s01_proposal_number": (content.slide01.proposal_number),
            "sv_s01_date": (content.slide01.date),
        }

        for shape_name, value in values.items():
            renderer.set_text_preserving_style(
                shape_name,
                value,
            )

    def _render_slide02(
        self,
        content: TemplateV2PresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        issues = content.slide02.issues

        for index in range(1, 6):
            shape_name = f"sv_s02_issue_{index}"

            if index <= len(issues):
                issue = issues[index - 1]

                renderer.set_keyword_detail_preserving_style(
                    shape_name,
                    keyword=issue.keyword,
                    detail=issue.detail,
                )
            else:
                renderer.set_text_preserving_style(
                    shape_name,
                    "",
                )

        renderer.lock_text_box_geometry(
            "sv_s02_issue_6",
            word_wrap=True,
        )

        renderer.set_impact_statement_preserving_style(
            "sv_s02_issue_6",
            content.slide02.impact_statement,
        )

    def _render_slide03(
        self,
        content: TemplateV2PresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        solutions = content.slide03.solutions

        solution_count = len(solutions)

        TemplateV2LayoutRenderer().render_slide03_solutions(
            renderer=renderer,
            active_count=solution_count,
        )

        single_line_indices = {
            1,
            4,
            5,
            6,
        }

        for index, solution in enumerate(
            solutions,
            start=1,
        ):
            shape_name = f"sv_s03_solution_{index}"

            renderer.lock_text_box_geometry(
                shape_name,
                word_wrap=(index not in single_line_indices),
            )

            renderer.set_text_preserving_style(
                shape_name,
                solution.text,
            )

        renderer.lock_text_box_geometry(
            "sv_s03_main_benefit",
            word_wrap=True,
        )

        renderer.lock_text_box_geometry(
            "sv_s03_main_benefit_secondary",
            word_wrap=True,
        )

        renderer.lock_text_box_geometry(
            "sv_s03_benefit_claim",
            word_wrap=True,
        )

        renderer.set_paragraph_text_preserving_style(
            "sv_s03_main_benefit",
            1,
            content.slide03.main_benefit,
        )

        renderer.set_text_preserving_style(
            "sv_s03_main_benefit_secondary",
            content.slide03.secondary_benefit,
        )

        renderer.set_text_preserving_style(
            "sv_s03_benefit_claim",
            content.slide03.benefit_claim,
        )

        for index in range(
            solution_count + 1,
            7,
        ):
            renderer.remove_shape(f"sv_s03_solution_{index}")

            renderer.remove_shape(f"sv_s03_solution_{index}_icon")

    def _render_slide07(
        self,
        content: TemplateV2PresentationContent,
        renderer: PowerPointRenderer,
    ) -> None:
        # Párrafo 0 ("Resumen del proyecto")
        # se mantiene fijo.
        #
        # Los párrafos 1..5 son dinámicos.

        for index in range(
            5,
        ):
            text = (
                content.slide07.project_summary[index]
                if index < len(content.slide07.project_summary)
                else ""
            )

            renderer.set_paragraph_text_preserving_style(
                "sv_s07_project_summary",
                index + 1,
                text,
            )

        # Presupuesto:
        # P0 fijo
        # P1 importe
        # P2 IVA + fecha
        # P3 encabezado pago
        # P4-P5 condiciones

        renderer.set_paragraph_text_preserving_style(
            "sv_s07_budget_block",
            1,
            content.slide07.budget_amount,
        )

        renderer.set_paragraph_text_preserving_style(
            "sv_s07_budget_block",
            2,
            ("IVA incluido · Válido hasta " f"{content.slide07.budget_valid_until}"),
        )

        payment_terms = content.slide07.payment_terms

        first_payment_block = ""

        if payment_terms:
            first_payment_block = payment_terms[0]

        if len(payment_terms) >= 2:
            first_payment_block += " " + payment_terms[1]

        renderer.set_paragraph_text_preserving_style(
            "sv_s07_budget_block",
            4,
            first_payment_block,
        )

        renderer.set_paragraph_text_preserving_style(
            "sv_s07_budget_block",
            5,
            (payment_terms[2] if len(payment_terms) >= 3 else ""),
        )
