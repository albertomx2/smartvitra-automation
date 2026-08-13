from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.cases.repository import CaseRepository
from backend.cases.schemas import (
    CaseWorkspacePhoto,
    CaseWorkspaceProject,
    CaseWorkspaceRead,
    CaseWorkspaceWindow,
)
from backend.db.models import (
    CasePhoto,
    CaseWindow,
    ProjectCase,
)
from backend.integrations.prefweb.service import (
    PrefWebService,
)


class CaseNotFoundError(LookupError):
    pass


class CaseWindowNotFoundError(LookupError):
    pass


class CasePhotoNotFoundError(LookupError):
    pass


class ProjectCaseService:
    def __init__(
        self,
        db: Session,
        prefweb_service: PrefWebService | None = None,
    ) -> None:
        self._repository = CaseRepository(db)

        self._prefweb = prefweb_service or PrefWebService()

    def create_from_prefweb(
        self,
        *,
        number: int,
        version: int,
    ) -> ProjectCase:
        existing = self._repository.get_by_prefweb_document(
            number=number,
            version=version,
        )

        if existing is not None:
            return existing

        project = self._prefweb.get_project_by_number(
            number=number,
            version=version,
        )

        case = ProjectCase(
            prefweb_number=project.number,
            prefweb_version=project.version,
            alias_number=project.alias_number,
            customer_name=project.customer_name,
            status="draft",
        )

        case.windows = [
            CaseWindow(
                prefweb_item_id=window.item_id,
                prefweb_id_pos=window.id_pos,
                position=window.position,
                room=window.room,
            )
            for window in project.windows
        ]

        return self._repository.add(case)

    def get_case(
        self,
        *,
        case_id: uuid.UUID,
    ) -> ProjectCase:
        case = self._repository.get(
            case_id=case_id,
        )

        if case is None:
            raise CaseNotFoundError(f"Case {case_id} not found")

        return case

    def sync_windows_from_prefweb(
        self,
        *,
        case: ProjectCase,
        project,
    ) -> ProjectCase:
        existing_windows = self._repository.get_windows(
            case_id=case.id,
        )

        existing_by_item_id = {
            window.prefweb_item_id: window for window in existing_windows
        }

        changed = False

        for prefweb_window in project.windows:
            item_id = prefweb_window.item_id

            if not item_id:
                continue

            existing = existing_by_item_id.get(
                item_id,
            )

            if existing is None:
                case.windows.append(
                    CaseWindow(
                        prefweb_item_id=item_id,
                        prefweb_id_pos=prefweb_window.id_pos,
                        position=prefweb_window.position,
                        room=prefweb_window.room,
                    )
                )

                changed = True
                continue

            if existing.prefweb_id_pos != prefweb_window.id_pos:
                existing.prefweb_id_pos = prefweb_window.id_pos
                changed = True

            if existing.position != prefweb_window.position:
                existing.position = prefweb_window.position
                changed = True

            if not existing.room and prefweb_window.room:
                existing.room = prefweb_window.room
                changed = True

        if changed:
            self._repository.commit()

            refreshed = self._repository.get(
                case_id=case.id,
            )

            if refreshed is not None:
                return refreshed

        return case

    def get_workspace(
        self,
        *,
        case_id: uuid.UUID,
    ) -> CaseWorkspaceRead:
        case = self.get_case(
            case_id=case_id,
        )

        project = self._prefweb.get_project_by_number(
            number=case.prefweb_number,
            version=case.prefweb_version,
        )

        case = self.sync_windows_from_prefweb(
            case=case,
            project=project,
        )

        case_windows_by_item_id = {
            window.prefweb_item_id: window for window in case.windows
        }

        photos = self._repository.list_photos(
            case_id=case_id,
        )

        photos_by_window_id: dict[
            uuid.UUID,
            list[CaseWorkspacePhoto],
        ] = {}

        for photo in photos:
            if photo.window_id is None:
                continue

            photos_by_window_id.setdefault(
                photo.window_id,
                [],
            ).append(
                CaseWorkspacePhoto(
                    id=photo.id,
                    filename=photo.original_filename,
                    content_type=photo.content_type,
                    description=photo.description,
                    file_url=(f"/api/cases/{case.id}/photos/" f"{photo.id}/file"),
                )
            )

        windows: list[CaseWorkspaceWindow] = []

        for prefweb_window in project.windows:
            prefweb_item_id = prefweb_window.item_id

            if not prefweb_item_id:
                continue

            case_window = case_windows_by_item_id.get(
                prefweb_item_id,
            )

            if case_window is None:
                continue

            windows.append(
                CaseWorkspaceWindow(
                    id=case_window.id,
                    prefweb_item_id=prefweb_item_id,
                    prefweb_id_pos=prefweb_window.id_pos,
                    position=prefweb_window.position,
                    nomenclature=prefweb_window.nomenclature,
                    reference=prefweb_window.reference,
                    description=prefweb_window.description,
                    color=prefweb_window.color,
                    dimensions=prefweb_window.dimensions,
                    quantity=prefweb_window.quantity,
                    total_amount=prefweb_window.total_amount,
                    room=case_window.room,
                    problem_type=case_window.problem_type,
                    commercial_notes=case_window.commercial_notes,
                    prefweb_svg_url=(
                        f"/api/prefweb/projects/"
                        f"{project.number}/versions/"
                        f"{project.version}/windows/"
                        f"{prefweb_window.item_id}/svg"
                    ),
                    photos=photos_by_window_id.get(
                        case_window.id,
                        [],
                    ),
                )
            )

        return CaseWorkspaceRead(
            id=case.id,
            status=case.status,
            visit_notes=case.visit_notes,
            project=CaseWorkspaceProject(
                number=project.number,
                version=project.version,
                alias_number=project.alias_number,
                version_name=project.version_name,
                customer_name=project.customer_name,
                request_date=project.request_date,
                reference=project.reference,
                customer_address=project.customer_address,
                customer_address2=project.customer_address2,
                customer_postal_code=project.customer_postal_code,
                customer_city=project.customer_city,
                customer_country=project.customer_country,
                subtotal=project.subtotal,
                tax=project.tax,
                final_price=project.final_price,
                currency_symbol=project.currency_symbol,
            ),
            windows=windows,
        )

    def update_window(
        self,
        *,
        case_id: uuid.UUID,
        window_id: uuid.UUID,
        problem_type: str | None,
        commercial_notes: str | None,
    ) -> CaseWindow:
        window = self._repository.get_window(
            case_id=case_id,
            window_id=window_id,
        )

        if window is None:
            raise CaseWindowNotFoundError(f"Window {window_id} not found")

        window.problem_type = problem_type
        window.commercial_notes = commercial_notes

        self._repository.commit()

        return window

    def update_case(
        self,
        *,
        case_id: uuid.UUID,
        visit_notes: str | None,
    ) -> ProjectCase:
        case = self.get_case(
            case_id=case_id,
        )

        case.visit_notes = visit_notes

        self._repository.commit()

        return self.get_case(
            case_id=case_id,
        )

    def create_photo(
        self,
        *,
        case_id: uuid.UUID,
        original_filename: str,
        storage_key: str,
        content_type: str,
        size_bytes: int,
        description: str | None,
        window_id: uuid.UUID | None,
    ) -> CasePhoto:
        self.get_case(
            case_id=case_id,
        )

        if window_id is not None:
            window = self._repository.get_window(
                case_id=case_id,
                window_id=window_id,
            )

            if window is None:
                raise CaseWindowNotFoundError(f"Window {window_id} not found")

        photo = CasePhoto(
            case_id=case_id,
            window_id=window_id,
            original_filename=original_filename,
            storage_key=storage_key,
            content_type=content_type,
            size_bytes=size_bytes,
            description=description,
        )

        return self._repository.add_photo(photo)

    def delete_photo(
        self,
        *,
        case_id: uuid.UUID,
        photo_id: uuid.UUID,
    ) -> CasePhoto:
        photo = self._repository.get_photo(
            case_id=case_id,
            photo_id=photo_id,
        )

        if photo is None:
            raise CasePhotoNotFoundError(f"Photo {photo_id} not found")

        self._repository.delete_photo(photo)

        return photo

    def get_photo(
        self,
        *,
        case_id: uuid.UUID,
        photo_id: uuid.UUID,
    ) -> CasePhoto:
        photo = self._repository.get_photo(
            case_id=case_id,
            photo_id=photo_id,
        )

        if photo is None:
            raise CasePhotoNotFoundError(f"Photo {photo_id} not found")

        return photo

    def update_photo(
        self,
        *,
        case_id: uuid.UUID,
        photo_id: uuid.UUID,
        description: str | None,
    ) -> CasePhoto:
        photo = self._repository.get_photo(
            case_id=case_id,
            photo_id=photo_id,
        )

        if photo is None:
            raise CasePhotoNotFoundError(f"Photo {photo_id} not found")

        photo.description = description

        self._repository.commit_and_refresh(photo)

        return photo
