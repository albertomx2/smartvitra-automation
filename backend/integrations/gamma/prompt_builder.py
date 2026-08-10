from backend.presentation.models import (
    PresentationSlide,
    PresentationSpec,
)


class GammaPromptBuilder:
    def build(
        self,
        spec: PresentationSpec,
    ) -> str:
        sections = [self._header(spec)]

        for slide in spec.slides:
            sections.append(self._slide_section(slide))

        sections.append(self._global_rules())

        return "\n\n".join(sections)

    def _header(
        self,
        spec: PresentationSpec,
    ) -> str:
        return (
            "# SMARTVITRA PRESENTATION DATA\n\n"
            f"Customer: {spec.customer_name}\n"
            f"Proposal: {spec.proposal_number or ''}\n\n"
            "Use the existing SmartVitra template.\n"
            "Keep exactly the same 12-card commercial "
            "narrative and card order."
        )

    def _slide_section(
        self,
        slide: PresentationSlide,
    ) -> str:
        lines = [
            (f"## SLIDE {slide.position:02d} " f"- {slide.slide_type.value}"),
            f"Title: {slide.title}",
            f"Mode: {slide.mode.value}",
        ]

        if slide.subtitle:
            lines.append(f"Subtitle: {slide.subtitle}")

        if slide.locked:
            lines.append(
                "LOCKED: Preserve this template card. "
                "Do not rewrite its fixed content."
            )

        if slide.facts:
            lines.append("DATA:")

            for key, value in slide.facts.items():
                lines.append(f"- {key}: {value}")

        if slide.photos:
            lines.append("IMAGES:")

            for photo in slide.photos:
                lines.append(
                    "- "
                    f"role={photo.role}; "
                    f"opening={photo.opening_id}; "
                    f"source={photo.storage_key}"
                )

        if slide.requires_generated_image:
            lines.append(
                "GENERATED IMAGE REQUIRED: "
                "Do not invent this image. "
                "Use only the approved supplied AFTER "
                "image when available."
            )

        return "\n".join(lines)

    def _global_rules(
        self,
    ) -> str:
        return (
            "# GLOBAL RULES\n\n"
            "- Keep exactly 12 cards.\n"
            "- Preserve the order of the template.\n"
            "- Do not invent prices.\n"
            "- Do not invent products.\n"
            "- Do not invent technical claims.\n"
            "- Do not invent savings percentages.\n"
            "- Do not invent warranties or promotions.\n"
            "- Preserve fixed cards.\n"
            "- Use customer-specific data only in the "
            "corresponding dynamic cards.\n"
            "- All monetary values must remain exact."
        )
