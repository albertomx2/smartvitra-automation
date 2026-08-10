from backend.commercial.models import (
    BriefPhoto,
    CommercialBrief,
)
from backend.presentation.enums import (
    SlideMode,
    SlideType,
)
from backend.presentation.models import (
    PresentationSlide,
    PresentationSpec,
    SlidePhotoReference,
)


class PresentationSpecBuilder:
    def build(
        self,
        brief: CommercialBrief,
    ) -> PresentationSpec:
        slides = [
            self._slide_01_cover(),
            self._slide_02_current_situation(brief),
            self._slide_03_consequences(brief),
            self._slide_04_problem_confirmation(brief),
            self._slide_05_solution_transition(),
            self._slide_06_proposal(brief),
            self._slide_07_benefits(brief),
            self._slide_08_before_after(brief),
            self._slide_09_why_smartvitra(),
            self._slide_10_investment(brief),
            self._slide_11_final_price(brief),
            self._slide_12_closing(),
        ]

        return PresentationSpec(
            proposal_number=(brief.proposal_number),
            customer_name=(brief.customer.name),
            slides=slides,
        )

    def _slide_01_cover(
        self,
    ) -> PresentationSlide:
        return PresentationSlide(
            position=1,
            slide_type=SlideType.COVER,
            mode=SlideMode.FIXED,
            title="SmartVitra",
            template_key="cover",
            locked=True,
        )

    def _slide_02_current_situation(
        self,
        brief: CommercialBrief,
    ) -> PresentationSlide:
        needs = []

        if brief.primary_need is not None:
            needs.append(brief.primary_need.model_dump(mode="json"))

        needs.extend(need.model_dump(mode="json") for need in brief.secondary_needs)

        return PresentationSlide(
            position=2,
            slide_type=(SlideType.CURRENT_SITUATION),
            mode=SlideMode.DYNAMIC,
            title="¿Cómo está tu vivienda?",
            subtitle=("Sabemos lo que estás " "viviendo cada día en casa"),
            requires_ai_text=True,
            facts={
                "needs": needs,
            },
            photos=self._photos_for_usage(
                brief,
                "current_problem",
            ),
        )

    def _slide_03_consequences(
        self,
        brief: CommercialBrief,
    ) -> PresentationSlide:
        need_codes = []

        if brief.primary_need is not None:
            need_codes.append(brief.primary_need.code)

        need_codes.extend(need.code for need in brief.secondary_needs)

        return PresentationSlide(
            position=3,
            slide_type=SlideType.CONSEQUENCES,
            mode=SlideMode.SEMI_DYNAMIC,
            title=("¿Qué pasa si no haces nada?"),
            requires_ai_text=True,
            facts={
                "need_codes": need_codes,
            },
        )

    def _slide_04_problem_confirmation(
        self,
        brief: CommercialBrief,
    ) -> PresentationSlide:
        primary_need = None

        if brief.primary_need is not None:
            primary_need = brief.primary_need.model_dump(mode="json")

        return PresentationSlide(
            position=4,
            slide_type=(SlideType.PROBLEM_CONFIRMATION),
            mode=SlideMode.DYNAMIC,
            title=("¿Este es realmente el " "problema en tu vivienda?"),
            requires_ai_text=True,
            facts={
                "primary_need": primary_need,
            },
            photos=self._photos_for_usage(
                brief,
                "problem_confirmation",
            ),
        )

    def _slide_05_solution_transition(
        self,
    ) -> PresentationSlide:
        return PresentationSlide(
            position=5,
            slide_type=(SlideType.SOLUTION_TRANSITION),
            mode=SlideMode.FIXED,
            title=("¿Quieres que te ayudemos " "a solucionarlo?"),
            template_key=("solution_transition"),
            locked=True,
        )

    def _slide_06_proposal(
        self,
        brief: CommercialBrief,
    ) -> PresentationSlide:
        return PresentationSlide(
            position=6,
            slide_type=SlideType.PROPOSAL,
            mode=SlideMode.DYNAMIC,
            title=("Nuestra propuesta para " "tu vivienda"),
            requires_ai_text=True,
            facts={
                "openings": [
                    opening.model_dump(mode="json") for opening in brief.openings
                ],
                "products": [
                    product.model_dump(mode="json") for product in brief.products
                ],
                "services": [
                    service.model_dump(mode="json") for service in brief.services
                ],
            },
            photos=self._photos_for_usage(
                brief,
                "proposal",
            ),
        )

    def _slide_07_benefits(
        self,
        brief: CommercialBrief,
    ) -> PresentationSlide:
        benefits: dict[
            str,
            dict,
        ] = {}

        for product in brief.products:
            for benefit in product.benefits:
                benefits.setdefault(
                    benefit.code,
                    benefit.model_dump(mode="json"),
                )

        return PresentationSlide(
            position=7,
            slide_type=SlideType.BENEFITS,
            mode=SlideMode.DYNAMIC,
            title=("Lo que vas a notar " "desde el primer día"),
            requires_ai_text=True,
            facts={
                "benefits": list(benefits.values()),
            },
        )

    def _slide_08_before_after(
        self,
        brief: CommercialBrief,
    ) -> PresentationSlide:
        photos = self._photos_for_usage(
            brief,
            "before_after",
        )

        return PresentationSlide(
            position=8,
            slide_type=SlideType.BEFORE_AFTER,
            mode=SlideMode.DYNAMIC,
            title="Una decisión cambia todo",
            requires_ai_text=False,
            requires_generated_image=bool(photos),
            facts={
                "generation_status": ("pending" if photos else "not_available"),
            },
            photos=photos,
        )

    def _slide_09_why_smartvitra(
        self,
    ) -> PresentationSlide:
        return PresentationSlide(
            position=9,
            slide_type=(SlideType.WHY_SMARTVITRA),
            mode=SlideMode.FIXED,
            title=("¿Por qué trabajar " "con nosotros?"),
            template_key="why_smartvitra",
            locked=True,
        )

    def _slide_10_investment(
        self,
        brief: CommercialBrief,
    ) -> PresentationSlide:
        pricing = brief.pricing

        return PresentationSlide(
            position=10,
            slide_type=SlideType.INVESTMENT,
            mode=SlideMode.SEMI_DYNAMIC,
            title="Tu inversión",
            facts={
                "usual_cost": (pricing.usual_cost if pricing is not None else None),
                "currency": (pricing.currency if pricing is not None else None),
            },
        )

    def _slide_11_final_price(
        self,
        brief: CommercialBrief,
    ) -> PresentationSlide:
        pricing = brief.pricing

        return PresentationSlide(
            position=11,
            slide_type=SlideType.FINAL_PRICE,
            mode=SlideMode.SEMI_DYNAMIC,
            title="Tu precio final",
            facts={
                "subtotal": (pricing.subtotal if pricing is not None else None),
                "tax_total": (pricing.tax_total if pricing is not None else None),
                "total": (pricing.total if pricing is not None else None),
                "discount_total": (
                    pricing.discount_total if pricing is not None else None
                ),
                "payment_terms": (
                    pricing.payment_terms if pricing is not None else None
                ),
            },
        )

    def _slide_12_closing(
        self,
    ) -> PresentationSlide:
        return PresentationSlide(
            position=12,
            slide_type=SlideType.CLOSING,
            mode=SlideMode.FIXED,
            title="¿Empezamos?",
            template_key="closing",
            locked=True,
        )

    def _photos_for_usage(
        self,
        brief: CommercialBrief,
        usage: str,
    ) -> list[SlidePhotoReference]:
        return [
            self._photo_reference(
                photo,
                usage,
            )
            for photo in brief.photos
            if usage in photo.usage
        ]

    def _photo_reference(
        self,
        photo: BriefPhoto,
        role: str,
    ) -> SlidePhotoReference:
        return SlidePhotoReference(
            photo_id=photo.photo_id,
            storage_key=photo.storage_key,
            opening_id=photo.opening_id,
            role=role,
            is_ai_generated=(photo.is_ai_generated),
        )
