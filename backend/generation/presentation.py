from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from backend.generation.payment_terms import (
    resolve_payment_terms,
)
from backend.generation.snapshot import (
    CaseGenerationSnapshot,
)
from backend.integrations.google_maps.street_view import (
    GoogleStreetViewFacadeClient,
)
from backend.integrations.image_generation.prefweb_reference import (
    render_prefweb_svg_reference,
)
from backend.integrations.image_generation.prompts import (
    build_solution_image_prompt,
)
from backend.integrations.image_generation.scene_selector import (
    SolutionImageScene,
    SolutionImageSceneSelector,
)
from backend.integrations.image_generation.vertex import (
    VertexSolutionImageClient,
)
from backend.integrations.llm.gemini import (
    GeminiStructuredClient,
)
from backend.integrations.prefweb.service import (
    PrefWebService,
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

        # Budget validity is not yet available
        # from the current PrefWeb integration.
        #
        # Payment terms come deterministically
        # from the real PrefWeb document.
        deterministic = TemplateV2DeterministicData(
            customer_name=(project.customer_name),
            address=address,
            proposal_number=(project.alias_number),
            proposal_date=(proposal_date),
            budget_amount=Decimal(str(project.final_price)),
            budget_valid_until=None,
            payment_terms=resolve_payment_terms(project.payment_term),
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

        # Select one real customer/window scene.
        #
        # This exact scene is used for BOTH:
        # - slide 2: current/problem photograph;
        # - slide 3: AI-generated proposed result.
        #
        # Therefore the AI transformation always corresponds
        # to the same PrefWeb window as the displayed photo.
        scene = SolutionImageSceneSelector().select(
            snapshot,
        )

        source_photo: Path | None = None

        if scene is not None:
            source_photo = self._get_scene_photo_path(
                scene,
            )

        if scene is not None and source_photo is not None:
            result["problem_photo"] = source_photo

            result["generated_solution"] = self._generate_solution_image(
                snapshot=snapshot,
                scene=scene,
                source_photo=source_photo,
                work_dir=work_dir,
            )
        elif photo_paths:
            # Legacy fallback when no window has both
            # problem metadata and a linked photograph.
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

        return result

    @staticmethod
    def _get_scene_photo_path(
        scene: SolutionImageScene,
    ) -> Path | None:
        storage = LocalFileStorage()

        path = storage.get_path(
            storage_key=scene.photo.storage_key,
        )

        if not path.exists():
            return None

        return path

    @staticmethod
    def _generate_solution_image(
        *,
        snapshot: CaseGenerationSnapshot,
        scene: SolutionImageScene,
        source_photo: Path,
        work_dir: Path,
    ) -> Path:
        solution_dir = work_dir / "solution_image"

        solution_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        prefweb = PrefWebService()

        svg = prefweb.get_window_svg(
            number=snapshot.project.number,
            version=snapshot.project.version,
            item_id=scene.window.prefweb_item_id,
        )

        reference_path = render_prefweb_svg_reference(
            svg=svg,
            output_path=(solution_dir / "prefweb_window_reference.png"),
        )

        prompt = build_solution_image_prompt(
            window=scene.window,
        )

        return VertexSolutionImageClient().generate(
            source_photo=source_photo,
            window_reference=reference_path,
            prompt=prompt,
            output_path=(solution_dir / "generated_solution.png"),
        )

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
