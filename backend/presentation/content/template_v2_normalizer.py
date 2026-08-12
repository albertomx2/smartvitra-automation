from backend.presentation.content.template_v2 import (
    TemplateV2PresentationContent,
)


class TemplateV2ContentNormalizer:
    def normalize(
        self,
        content: TemplateV2PresentationContent,
    ) -> TemplateV2PresentationContent:
        normalized = content.model_copy(deep=True)

        normalized.slide01.intro_text = normalized.slide01.intro_text.strip()

        normalized.slide01.customer_name = normalized.slide01.customer_name.strip()

        normalized.slide01.address = normalized.slide01.address.strip()

        normalized.slide01.proposal_number = normalized.slide01.proposal_number.strip()

        normalized.slide01.date = normalized.slide01.date.strip()

        for issue in normalized.slide02.issues:
            issue.keyword = issue.keyword.strip()

            issue.detail = issue.detail.strip()

        normalized.slide02.impact_statement = (
            normalized.slide02.impact_statement.strip()
        )

        for solution in normalized.slide03.solutions:
            solution.text = solution.text.strip()

            solution.icon_key = solution.icon_key.strip()

        normalized.slide03.main_benefit = normalized.slide03.main_benefit.strip()

        normalized.slide03.secondary_benefit = (
            normalized.slide03.secondary_benefit.strip()
        )

        normalized.slide03.benefit_claim = normalized.slide03.benefit_claim.strip()

        normalized.slide07.project_summary = [
            value.strip() for value in (normalized.slide07.project_summary)
        ]

        return normalized
