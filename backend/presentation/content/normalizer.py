from backend.presentation.content.models import (
    GeneratedPresentationContent,
)


class PresentationContentNormalizer:
    def normalize(
        self,
        content: GeneratedPresentationContent,
    ) -> GeneratedPresentationContent:
        normalized = content.model_copy(deep=True)

        normalized.benefit_icons = sorted(
            normalized.benefit_icons,
            key=lambda benefit_icon: (benefit_icon.benefit_index),
        )

        return normalized
