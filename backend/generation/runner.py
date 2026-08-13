from __future__ import annotations

import traceback

from sqlalchemy.orm import Session

from backend.generation.context_builder import (
    GenerationContextBuilder,
)
from backend.generation.presentation import (
    RealPresentationGenerator,
)
from backend.generation.repository import (
    GenerationJobRepository,
)
from backend.generation.service import (
    GenerationJobService,
)
from backend.generation.snapshot_builder import (
    GenerationSnapshotBuilder,
)
from backend.storage.generated import (
    GeneratedFileStorage,
)


class GenerationJobRunner:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self._db = db

        self._repository = GenerationJobRepository(db)

        self._service = GenerationJobService(db)

    def run_next(
        self,
    ) -> bool:
        job = self._repository.get_next_queued()

        if job is None:
            return False

        try:
            self._service.mark_running(job)

            self._service.update_progress(
                job,
                step="snapshotting",
                progress=10,
            )

            snapshot = GenerationSnapshotBuilder(self._db).build(
                case_id=job.case_id,
            )

            job.input_snapshot = snapshot.to_json_dict()

            self._repository.commit()

            self._service.update_progress(
                job,
                step=("building_context"),
                progress=25,
            )

            context = GenerationContextBuilder().build(snapshot)

            self._service.update_progress(
                job,
                step=("generating_content"),
                progress=40,
            )

            storage = GeneratedFileStorage()

            work_dir = storage.build_job_directory(
                case_id=job.case_id,
                job_id=job.id,
            )

            output_filename = (
                "SmartVitra_" f"{snapshot.project.alias_number}" ".pptx"
            ).replace("/", "-")

            output_path = work_dir / output_filename

            self._service.update_progress(
                job,
                step=("rendering_presentation"),
                progress=60,
            )

            RealPresentationGenerator().generate(
                snapshot=snapshot,
                context=context,
                output_path=output_path,
                work_dir=work_dir,
            )

            self._service.update_progress(
                job,
                step="saving_output",
                progress=90,
            )

            storage_key = storage.relative_key(output_path)

            self._service.mark_completed(
                job,
                storage_key=storage_key,
                filename=output_filename,
            )

            return True

        except Exception as exc:  # noqa: BLE001
            message = f"{type(exc).__name__}: " f"{exc}\n\n" f"{traceback.format_exc()}"

            self._service.mark_failed(
                job,
                error=message,
            )

            return True
