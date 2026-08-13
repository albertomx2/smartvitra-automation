from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.cases.repository import (
    CaseRepository,
)
from backend.generation.snapshot import (
    CaseGenerationSnapshot,
    GenerationPhotoSnapshot,
    GenerationProjectSnapshot,
    GenerationReferencePhotoSnapshot,
    GenerationWindowSnapshot,
)
from backend.integrations.prefweb.service import (
    PrefWebService,
)
from backend.reference_photos.repository import (
    ReferencePhotoRepository,
)


class GenerationSnapshotBuilder:
    def __init__(
        self,
        db: Session,
        prefweb_service: PrefWebService | None = None,
    ) -> None:
        self._db = db

        self._cases = CaseRepository(db)

        self._prefweb = prefweb_service or PrefWebService()

    def build(
        self,
        *,
        case_id: uuid.UUID,
    ) -> CaseGenerationSnapshot:
        case = self._cases.get(
            case_id=case_id,
        )

        if case is None:
            raise LookupError(f"Case {case_id} not found")

        # IMPORTANT:
        # PrefWeb is queried here, at generation time.
        # Therefore changes made in PrefWeb before pressing
        # Generate are reflected in this immutable snapshot.
        project = self._prefweb.get_project_by_number(
            number=case.prefweb_number,
            version=case.prefweb_version,
        )

        case_windows = {window.prefweb_item_id: window for window in case.windows}

        photos = self._cases.list_photos(
            case_id=case_id,
        )

        photos_by_window: dict[
            uuid.UUID,
            list[GenerationPhotoSnapshot],
        ] = {}

        for photo in photos:
            if photo.window_id is None:
                continue

            photos_by_window.setdefault(
                photo.window_id,
                [],
            ).append(
                GenerationPhotoSnapshot(
                    id=photo.id,
                    window_id=photo.window_id,
                    filename=photo.original_filename,
                    storage_key=photo.storage_key,
                    content_type=photo.content_type,
                    description=photo.description,
                )
            )

        windows: list[GenerationWindowSnapshot] = []

        for prefweb_window in project.windows:
            item_id = prefweb_window.item_id

            if not item_id:
                continue

            case_window = case_windows.get(
                item_id,
            )

            if case_window is None:
                # Window added in PrefWeb but case was not
                # refreshed yet. Preserve it anyway in the
                # generation snapshot.
                windows.append(
                    GenerationWindowSnapshot(
                        id=uuid.uuid4(),
                        prefweb_item_id=item_id,
                        prefweb_id_pos=(prefweb_window.id_pos),
                        position=(prefweb_window.position),
                        nomenclature=(prefweb_window.nomenclature),
                        reference=(prefweb_window.reference),
                        description=(prefweb_window.description),
                        color=prefweb_window.color,
                        dimensions=(prefweb_window.dimensions),
                        quantity=(prefweb_window.quantity),
                        total_amount=(prefweb_window.total_amount),
                        room=prefweb_window.room,
                    )
                )
                continue

            windows.append(
                GenerationWindowSnapshot(
                    id=case_window.id,
                    prefweb_item_id=item_id,
                    prefweb_id_pos=(prefweb_window.id_pos),
                    position=(prefweb_window.position),
                    nomenclature=(prefweb_window.nomenclature),
                    reference=(prefweb_window.reference),
                    description=(prefweb_window.description),
                    color=prefweb_window.color,
                    dimensions=(prefweb_window.dimensions),
                    quantity=(prefweb_window.quantity),
                    total_amount=(prefweb_window.total_amount),
                    room=(case_window.room or prefweb_window.room),
                    problem_type=(case_window.problem_type),
                    commercial_notes=(case_window.commercial_notes),
                    photos=(
                        photos_by_window.get(
                            case_window.id,
                            [],
                        )
                    ),
                )
            )

        reference_selections = ReferencePhotoRepository(self._db).get_selections(
            case_id=case_id
        )

        reference_photos = [
            GenerationReferencePhotoSnapshot(
                id=selection.reference_photo.id,
                slot=selection.slot,
                filename=(selection.reference_photo.original_filename),
                storage_key=(selection.reference_photo.storage_key),
                content_type=(selection.reference_photo.content_type),
                description=(selection.reference_photo.description),
            )
            for selection in reference_selections
        ]

        return CaseGenerationSnapshot(
            case_id=case.id,
            status=case.status,
            visit_notes=case.visit_notes,
            project=GenerationProjectSnapshot(
                number=project.number,
                version=project.version,
                alias_number=(project.alias_number),
                version_name=(project.version_name),
                customer_name=(project.customer_name),
                request_date=(project.request_date),
                reference=project.reference,
                customer_address=(project.customer_address),
                customer_address2=(project.customer_address2),
                customer_postal_code=(project.customer_postal_code),
                customer_city=(project.customer_city),
                customer_country=(project.customer_country),
                subtotal=project.subtotal,
                tax=project.tax,
                final_price=(project.final_price),
                currency_symbol=(project.currency_symbol),
            ),
            windows=windows,
            reference_photos=reference_photos,
        )
