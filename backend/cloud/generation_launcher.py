from __future__ import annotations

import os
import uuid

from google.cloud import run_v2


class GenerationLauncher:
    def __init__(
        self,
        *,
        backend: str | None = None,
        project_id: str | None = None,
        region: str | None = None,
        job_name: str | None = None,
    ) -> None:
        self._backend = (
            backend
            or os.getenv(
                "GENERATION_EXECUTION_BACKEND",
            )
            or "local"
        ).lower()

        self._project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or ""

        self._region = region or os.getenv("CLOUD_RUN_REGION") or "europe-west3"

        self._job_name = (
            job_name or os.getenv("CLOUD_RUN_GENERATION_JOB") or "smartvitra-generation"
        )

        if self._backend not in {
            "local",
            "cloud_run",
        }:
            raise RuntimeError(
                "Unsupported " "GENERATION_EXECUTION_BACKEND: " f"{self._backend}"
            )

    def launch(
        self,
        *,
        job_id: uuid.UUID,
    ) -> None:
        if self._backend == "local":
            return

        if not self._project_id:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT " "is not configured")

        client = run_v2.JobsClient()

        name = (
            f"projects/{self._project_id}/"
            f"locations/{self._region}/"
            f"jobs/{self._job_name}"
        )

        container_override = run_v2.RunJobRequest.Overrides.ContainerOverride(
            args=[
                "-m",
                "backend.workers.generation_worker",
                "--job-id",
                str(job_id),
            ]
        )

        overrides = run_v2.RunJobRequest.Overrides(
            container_overrides=[
                container_override,
            ],
        )

        request = run_v2.RunJobRequest(
            name=name,
            overrides=overrides,
        )

        client.run_job(
            request=request,
        )
