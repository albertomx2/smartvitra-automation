from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.cases.repository import CaseRepository
from backend.db.models.generation import (
    GenerationDelivery,
    GenerationJob,
)
from backend.generation.artifact_repository import (
    GenerationArtifactRepository,
)
from backend.generation.delivery_repository import (
    GenerationDeliveryRepository,
)
from backend.integrations.odoo import OdooClient
from backend.storage.generated import (
    GeneratedFileStorage,
)


class ProposalDeliveryError(RuntimeError):
    pass


from typing import ClassVar


class ProposalDeliveryService:
    SENDABLE_KINDS: ClassVar[set[str]] = {
        "presentation",
        "video",
        "attachment",
        "odoo_quote",
    }

    def __init__(
        self,
        db: Session,
    ) -> None:
        self._db = db
        self._cases = CaseRepository(db)
        self._artifacts = GenerationArtifactRepository(db)
        self._deliveries = GenerationDeliveryRepository(db)

    def send(
        self,
        *,
        job: GenerationJob,
    ) -> GenerationDelivery:
        if job.status != "completed":
            raise ProposalDeliveryError("Generation must be completed before delivery")

        existing = self._deliveries.get_sent_for_job(
            generation_job_id=job.id,
        )

        # Protección frente a doble click/reintento accidental.
        if existing is not None:
            return existing

        case = self._cases.get(
            case_id=job.case_id,
        )

        if case is None:
            raise ProposalDeliveryError("Project case not found")

        snapshot_project = (job.input_snapshot or {}).get("project") or {}
        recipient_name = (
            snapshot_project.get("customer_name") or case.customer_name
        ).strip()
        recipient_email = (
            snapshot_project.get("customer_email") or case.customer_email or ""
        ).strip()

        if not recipient_email:
            raise ProposalDeliveryError("Customer has no email address in PrefWeb")

        delivery = self._deliveries.add(
            GenerationDelivery(
                generation_job_id=job.id,
                status="sending",
                recipient_name=recipient_name,
                recipient_email=recipient_email,
            )
        )

        try:
            artifacts = [
                artifact
                for artifact in (
                    self._artifacts.list_for_job(
                        generation_job_id=job.id,
                    )
                )
                if artifact.kind in self.SENDABLE_KINDS
            ]

            kinds = {artifact.kind for artifact in artifacts}

            if "presentation" not in kinds:
                raise ProposalDeliveryError("Presentation artifact is missing")

            if "video" not in kinds:
                raise ProposalDeliveryError("Video artifact is missing")

            storage = GeneratedFileStorage()

            local_files = []

            for artifact in artifacts:
                path = storage.get_path(
                    storage_key=artifact.storage_key,
                )

                if not path.exists():
                    raise ProposalDeliveryError(
                        f"Artifact file not found: " f"{artifact.filename}"
                    )

                size = path.stat().st_size

                if size <= 0:
                    raise ProposalDeliveryError(
                        f"Artifact is empty: " f"{artifact.filename}"
                    )

                local_files.append(
                    (
                        artifact,
                        path,
                        size,
                    )
                )

            odoo = OdooClient()

            if job.odoo_partner_id is not None:
                partner_id = job.odoo_partner_id
                partner_created = bool(job.odoo_partner_created)
            else:
                # Older generations predate Odoo preparation at Generate time.
                partner, partner_created = odoo.find_or_create_partner(
                    name=recipient_name,
                    email=recipient_email,
                    phone=snapshot_project.get("customer_phone") or case.customer_phone,
                )
                partner_id = int(partner["id"])

            attachment_ids: list[int] = []

            sent_artifacts: list[dict[str, object]] = []

            for artifact, path, size in local_files:
                attachment_id = odoo.create_attachment(
                    filename=artifact.filename,
                    content=path.read_bytes(),
                    content_type=artifact.content_type,
                )

                attachment_ids.append(
                    attachment_id,
                )

                sent_artifacts.append(
                    {
                        "artifact_id": str(artifact.id),
                        "kind": artifact.kind,
                        "filename": artifact.filename,
                        "size_bytes": size,
                        "odoo_attachment_id": attachment_id,
                    }
                )

            mail_id = odoo.send_proposal_email(
                partner_id=partner_id,
                partner_name=recipient_name,
                attachment_ids=attachment_ids,
                has_manual_attachments=any(
                    artifact.kind == "attachment" for artifact in artifacts
                ),
                has_odoo_quote="odoo_quote" in kinds,
            )

            delivery.status = "sent"
            delivery.odoo_partner_id = partner_id
            delivery.odoo_mail_id = mail_id
            delivery.partner_created = partner_created
            delivery.attachment_count = len(attachment_ids)
            delivery.sent_artifacts = sent_artifacts
            delivery.error_message = None
            delivery.sent_at = datetime.now(
                timezone.utc,
            )

            self._deliveries.commit()
            self._deliveries.refresh(
                delivery,
            )

            return delivery

        except Exception as exc:
            delivery.status = "failed"
            delivery.error_message = f"{type(exc).__name__}: {exc}"

            self._deliveries.commit()

            raise
