from __future__ import annotations

import json
import traceback
import uuid

from sqlalchemy.orm import Session

from backend.db.models.generation import (
    GenerationArtifact,
    GenerationJob,
)
from backend.generation.artifact_repository import (
    GenerationArtifactRepository,
)
from backend.generation.context_builder import (
    GenerationContextBuilder,
)
from backend.generation.narration.elevenlabs import (
    ElevenLabsNarrationGenerator,
)
from backend.generation.narration.script import (
    NarrationScriptGenerator,
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
from backend.generation.video import (
    NarratedPresentationVideoRenderer,
)
from backend.integrations.llm.gemini import (
    GeminiStructuredClient,
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

        self._repository = GenerationJobRepository(
            db,
        )

        self._service = GenerationJobService(
            db,
        )

    def run_next(
        self,
    ) -> bool:
        """
        Legacy/local worker mode.

        Processes the oldest queued job.
        Returns False only when there is
        nothing to process.
        """

        job = self._repository.get_next_queued()

        if job is None:
            return False

        self._process_job(
            job,
        )

        return True

    def run_job(
        self,
        *,
        job_id: uuid.UUID,
    ) -> bool:
        """
        Process exactly one generation job.

        This is the entry point intended
        for Cloud Run Jobs.
        """

        job = self._repository.get(
            job_id=job_id,
        )

        if job is None:
            raise LookupError(f"Generation job " f"{job_id} not found")

        if job.status != "queued":
            raise RuntimeError(
                f"Generation job "
                f"{job_id} has status "
                f"{job.status!r}; "
                "expected 'queued'"
            )

        return self._process_job(
            job,
        )

    def _process_job(
        self,
        job: GenerationJob,
    ) -> bool:
        try:
            self._service.mark_running(
                job,
            )

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
                step="building_context",
                progress=25,
            )

            context = GenerationContextBuilder().build(snapshot)

            self._service.update_progress(
                job,
                step="generating_content",
                progress=40,
            )

            storage = GeneratedFileStorage()

            work_dir = storage.build_job_directory(
                case_id=job.case_id,
                job_id=job.id,
            )

            output_filename = (
                "SmartVitra_" f"{snapshot.project.alias_number}" ".pptx"
            ).replace(
                "/",
                "-",
            )

            output_path = work_dir / output_filename

            self._service.update_progress(
                job,
                step="rendering_presentation",
                progress=60,
            )

            presentation_result = RealPresentationGenerator().generate(
                snapshot=snapshot,
                context=context,
                output_path=output_path,
                work_dir=work_dir,
            )

            self._service.update_progress(
                job,
                step="generating_script",
                progress=72,
            )

            narration_script = NarrationScriptGenerator(
                GeminiStructuredClient(),
            ).generate(
                context=context,
                presentation_content=presentation_result.content,
            )

            self._service.update_progress(
                job,
                step="generating_narration",
                progress=78,
            )

            narration_dir = work_dir / "narration_slides"

            narration_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            tts = ElevenLabsNarrationGenerator()

            video_renderer = NarratedPresentationVideoRenderer()

            slide_audio_paths = []

            updated_slides = []

            for slide in narration_script.slides:
                slide_audio_path = narration_dir / (
                    f"slide_" f"{slide.slide_number:02d}" ".mp3"
                )

                tts.generate(
                    text=slide.narration,
                    output_path=(slide_audio_path),
                )

                duration = video_renderer.probe_duration(
                    path=slide_audio_path,
                )

                slide_audio_paths.append(slide_audio_path)

                updated_slides.append(
                    slide.model_copy(
                        update={
                            "audio_duration_seconds": duration,
                        }
                    )
                )

            actual_duration = sum(
                slide.audio_duration_seconds or 0.0 for slide in updated_slides
            )

            narration_script = narration_script.model_copy(
                update={
                    "slides": updated_slides,
                    "actual_duration_seconds": actual_duration,
                }
            )

            script_filename = (
                "SmartVitra_" f"{snapshot.project.alias_number}" "_script.json"
            ).replace(
                "/",
                "-",
            )

            script_path = work_dir / script_filename

            script_path.write_text(
                json.dumps(
                    narration_script.model_dump(
                        mode="json",
                    ),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            self._service.update_progress(
                job,
                step="rendering_video",
                progress=88,
            )

            video_filename = (
                "SmartVitra_" f"{snapshot.project.alias_number}" ".mp4"
            ).replace(
                "/",
                "-",
            )

            video_path = work_dir / video_filename

            narration_filename = (
                "SmartVitra_" f"{snapshot.project.alias_number}" "_narration.mp3"
            ).replace(
                "/",
                "-",
            )

            narration_path = work_dir / narration_filename

            video_renderer.render(
                presentation_path=output_path,
                slide_audio_paths=(slide_audio_paths),
                output_video_path=(video_path),
                output_audio_path=(narration_path),
                work_dir=work_dir,
            )

            self._service.update_progress(
                job,
                step="saving_outputs",
                progress=95,
            )

            presentation_content_type = (
                "application/vnd."
                "openxmlformats-officedocument."
                "presentationml.presentation"
            )

            presentation_storage_key = storage.persist(
                path=output_path,
                content_type=(presentation_content_type),
            )

            script_storage_key = storage.persist(
                path=script_path,
                content_type=("application/json"),
            )

            narration_storage_key = storage.persist(
                path=narration_path,
                content_type=("audio/mpeg"),
            )

            video_storage_key = storage.persist(
                path=video_path,
                content_type=("video/mp4"),
            )

            artifacts = GenerationArtifactRepository(
                self._db,
            )

            artifacts.add(
                GenerationArtifact(
                    generation_job_id=job.id,
                    kind="presentation",
                    filename=output_filename,
                    storage_key=(presentation_storage_key),
                    content_type=(presentation_content_type),
                    size_bytes=(output_path.stat().st_size),
                )
            )

            artifacts.add(
                GenerationArtifact(
                    generation_job_id=job.id,
                    kind="script",
                    filename=script_filename,
                    storage_key=(script_storage_key),
                    content_type=("application/json"),
                    size_bytes=(script_path.stat().st_size),
                )
            )

            artifacts.add(
                GenerationArtifact(
                    generation_job_id=job.id,
                    kind="narration",
                    filename=(narration_filename),
                    storage_key=(narration_storage_key),
                    content_type="audio/mpeg",
                    size_bytes=(narration_path.stat().st_size),
                )
            )

            artifacts.add(
                GenerationArtifact(
                    generation_job_id=job.id,
                    kind="video",
                    filename=video_filename,
                    storage_key=(video_storage_key),
                    content_type="video/mp4",
                    size_bytes=(video_path.stat().st_size),
                )
            )

            self._service.mark_completed(
                job,
                storage_key=(presentation_storage_key),
                filename=output_filename,
            )

            return True

        except Exception as exc:  # noqa: BLE001
            message = f"{type(exc).__name__}: " f"{exc}\n\n" f"{traceback.format_exc()}"

            self._service.mark_failed(
                job,
                error=message,
            )

            return False
