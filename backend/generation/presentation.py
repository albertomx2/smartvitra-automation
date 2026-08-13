from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from backend.generation.snapshot import (
    CaseGenerationSnapshot,
)
from backend.integrations.google_maps.street_view import (
    GoogleStreetViewFacadeClient,
)
from backend.integrations.llm.gemini import (
    GeminiStructuredClient,
)
from backend.presentation.content.template_v2_generator import (
    LLMTemplateV2ContentGenerator,
    TemplateV2DeterministicData,
)
from backend.presentation.content.template_v2_normalizer import (
    TemplateV2ContentNormalizer,
)
from backend.rendering.pptx.renderer import (
    PowerPointRenderer,
)
from backend.rendering.pptx.template_v2_content_renderer import (
    TemplateV2ContentRenderer,
)
from backend.rendering.pptx.template_v2_icon_renderer import (
    TemplateV2IconRenderer,
)
from backend.rendering.pptx.template_v2_image_renderer import (
    TemplateV2ImageRenderer,
)
from backend.storage.local import (
    LocalFileStorage,
)
from backend.storage.reference import (
    ReferencePhotoStorage,
)


class RealPresentationGenerator:
    TEMPLATE = Path("experiments/pptx_template/" "input/template.pptx")

    def generate(
        self,
        *,
        snapshot: CaseGenerationSnapshot,
        context: dict,
        output_path: Path,
        work_dir: Path,
    ) -> Path:
        project = snapshot.project

        address = self._build_address(snapshot)

        proposal_date = datetime.now(timezone.utc).date()

        # Temporary business-safe fallback.
        #
        # The real PrefWeb validity/payment
        # terms source will replace this.
        #
        # We do NOT use made-up percentages.
        deterministic = TemplateV2DeterministicData(
            customer_name=(project.customer_name),
            address=address,
            proposal_number=(project.alias_number),
            proposal_date=(proposal_date),
            budget_amount=Decimal(str(project.final_price)),
            budget_valid_until=None,
            payment_terms=["Condiciones de pago según presupuesto"],
        )

        generator = LLMTemplateV2ContentGenerator(GeminiStructuredClient())

        content = generator.generate(
            context=context,
            deterministic=deterministic,
        )

        content = TemplateV2ContentNormalizer().normalize(content)

        renderer = PowerPointRenderer(self.TEMPLATE)

        TemplateV2ContentRenderer().render(
            content,
            renderer,
        )

        TemplateV2IconRenderer().render(
            content,
            renderer,
        )

        images = self._build_images(
            snapshot=snapshot,
            work_dir=work_dir,
        )

        if images:
            TemplateV2ImageRenderer().render(
                renderer=renderer,
                images=images,
                work_dir=(work_dir / "normalized_images"),
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        renderer.save(output_path)

        return output_path

    def _build_images(
        self,
        *,
        snapshot: CaseGenerationSnapshot,
        work_dir: Path,
    ) -> dict[str, Path]:
        result: dict[str, Path] = {}

        photo_paths = self._get_real_photo_paths(snapshot)

        # Visit photo:
        # real current-state/problem image.
        if photo_paths:
            result["problem_photo"] = photo_paths[0]

        # Related SmartVitra projects:
        # selected explicitly in the workspace.
        reference_storage = ReferencePhotoStorage()

        for reference in sorted(
            snapshot.reference_photos,
            key=lambda item: item.slot,
        ):
            if not 1 <= reference.slot <= 3:
                continue

            path = reference_storage.get_path(storage_key=(reference.storage_key))

            if not path.exists():
                continue

            result[f"project_photo_" f"{reference.slot}"] = path

        facade = self._try_facade(
            snapshot=snapshot,
            work_dir=work_dir,
        )

        if facade is not None:
            result["cover_photo"] = facade
        elif photo_paths:
            result["cover_photo"] = photo_paths[0]

        # Do NOT fabricate AI result images yet.
        # Those slots will be wired to the future
        # image-generation stage.

        return result

    @staticmethod
    def _get_real_photo_paths(
        snapshot: CaseGenerationSnapshot,
    ) -> list[Path]:
        storage = LocalFileStorage()

        result: list[Path] = []

        for window in snapshot.windows:
            for photo in window.photos:
                path = storage.get_path(storage_key=(photo.storage_key))

                if path.exists():
                    result.append(path)

        return result

    @staticmethod
    def _build_address(
        snapshot: CaseGenerationSnapshot,
    ) -> str:
        project = snapshot.project

        street_parts = [
            project.customer_address,
            project.customer_address2,
        ]

        street = " ".join(
            value.strip() for value in street_parts if value and value.strip()
        )

        locality_parts = [
            project.customer_postal_code,
            project.customer_city,
        ]

        locality = " ".join(
            value.strip() for value in locality_parts if value and value.strip()
        )

        address_parts = [
            street,
            locality,
            project.customer_country,
        ]

        cleaned = [value.strip() for value in address_parts if value and value.strip()]

        if cleaned:
            return ", ".join(cleaned)

        return "Dirección no disponible"

    @staticmethod
    def _try_facade(
        *,
        snapshot: CaseGenerationSnapshot,
        work_dir: Path,
    ) -> Path | None:
        project = snapshot.project

        if not project.customer_address:
            return None

        address = RealPresentationGenerator._build_address(snapshot)

        try:
            client = GoogleStreetViewFacadeClient()

            return client.download_facade(
                address=address,
                output_path=(work_dir / "cover_facade.jpg"),
            )
        except (OSError, RuntimeError, ValueError):
            # Maps is enrichment, not a
            # critical dependency.
            return None
