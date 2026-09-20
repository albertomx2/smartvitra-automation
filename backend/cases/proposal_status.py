from __future__ import annotations

import uuid

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from backend.db.models.case import ProjectCase
from backend.db.models.generation import GenerationDelivery, GenerationJob


def classify_proposal_status(
    *, case_exists: bool, job_status: str | None, sent: bool
) -> str:
    if not case_exists:
        return "not_started"
    if job_status == "completed":
        return "sent" if sent else "generated"
    return "draft_in_progress"


def proposal_statuses_for_documents(
    db: Session, documents: list[tuple[int, int]]
) -> dict[tuple[int, int], str]:
    if not documents:
        return {}
    cases = db.scalars(
        select(ProjectCase).where(
            tuple_(ProjectCase.prefweb_number, ProjectCase.prefweb_version).in_(
                documents
            )
        )
    ).all()
    case_by_document = {
        (case.prefweb_number, case.prefweb_version): case for case in cases
    }
    case_ids = [case.id for case in cases]
    latest_by_case: dict[uuid.UUID, GenerationJob] = {}
    if case_ids:
        jobs = db.scalars(
            select(GenerationJob)
            .where(GenerationJob.case_id.in_(case_ids))
            .order_by(GenerationJob.created_at.desc(), GenerationJob.id.desc())
        ).all()
        for job in jobs:
            latest_by_case.setdefault(job.case_id, job)

    completed_ids = [
        job.id for job in latest_by_case.values() if job.status == "completed"
    ]
    sent_job_ids: set[uuid.UUID] = set()
    if completed_ids:
        sent_job_ids = set(
            db.scalars(
                select(GenerationDelivery.generation_job_id).where(
                    GenerationDelivery.generation_job_id.in_(completed_ids),
                    GenerationDelivery.status == "sent",
                )
            ).all()
        )

    statuses: dict[tuple[int, int], str] = {}
    for document in documents:
        case = case_by_document.get(document)
        latest_job: GenerationJob | None = (
            latest_by_case.get(case.id) if case is not None else None
        )
        statuses[document] = classify_proposal_status(
            case_exists=case is not None,
            job_status=latest_job.status if latest_job is not None else None,
            sent=latest_job.id in sent_job_ids if latest_job is not None else False,
        )
    return statuses
