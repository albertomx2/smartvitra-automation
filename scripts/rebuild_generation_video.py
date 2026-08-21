from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from pathlib import Path

from sqlalchemy import select

from backend.db.models.generation import (
    GenerationArtifact,
    GenerationJob,
)
from backend.db.session import SessionLocal
from backend.storage.generated import (
    GeneratedFileStorage,
)


def run(
    command: list[str],
) -> None:
    print("+", " ".join(command))

    subprocess.run(
        command,
        check=True,
    )


def get_artifact(
    artifacts: list[GenerationArtifact],
    kind: str,
) -> GenerationArtifact:
    for artifact in artifacts:
        if artifact.kind == kind:
            return artifact

    raise RuntimeError(f"Artifact {kind!r} not found")


def render_presentation(
    *,
    presentation_path: Path,
    render_dir: Path,
) -> list[Path]:
    render_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(render_dir),
            str(presentation_path),
        ]
    )

    pdf_path = render_dir / f"{presentation_path.stem}.pdf"

    if not pdf_path.exists():
        raise RuntimeError("LibreOffice did not create PDF")

    prefix = render_dir / "slide"

    run(
        [
            "pdftoppm",
            "-png",
            "-r",
            "180",
            str(pdf_path),
            str(prefix),
        ]
    )

    result = sorted(
        render_dir.glob("slide-*.png"),
        key=lambda path: int(path.stem.split("-")[-1]),
    )

    if len(result) < 9:
        raise RuntimeError(f"Expected 9 slides, found {len(result)}")

    return result[:9]


def build_silent_video(
    *,
    slide_images: list[Path],
    durations: list[float],
    output_path: Path,
    work_dir: Path,
) -> None:
    segments: list[Path] = []

    for index, (
        image_path,
        duration,
    ) in enumerate(
        zip(
            slide_images,
            durations,
            strict=True,
        ),
        start=1,
    ):
        segment = work_dir / f"silent_{index:02d}.mp4"

        run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-framerate",
                "30",
                "-i",
                str(image_path),
                "-t",
                f"{duration:.6f}",
                "-vf",
                (
                    "scale=1920:1080:"
                    "force_original_aspect_ratio=decrease,"
                    "pad=1920:1080:"
                    "(ow-iw)/2:(oh-ih)/2,"
                    "format=yuv420p"
                ),
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "20",
                "-r",
                "30",
                str(segment),
            ]
        )

        segments.append(segment)

    concat_file = work_dir / "silent_segments.txt"

    concat_file.write_text(
        "\n".join(f"file '{path.resolve()}'" for path in segments),
        encoding="utf-8",
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(output_path),
        ]
    )


def mux_audio(
    *,
    silent_video_path: Path,
    narration_path: Path,
    output_path: Path,
) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent_video_path),
            "-i",
            str(narration_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--job-id",
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        default="tmp/rebuild_video",
    )

    args = parser.parse_args()

    job_id = uuid.UUID(args.job_id)

    output_root = Path(args.output_dir) / str(job_id)

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    storage = GeneratedFileStorage()

    with SessionLocal() as db:
        job = db.scalar(select(GenerationJob).where(GenerationJob.id == job_id))

        if job is None:
            raise RuntimeError("Generation job not found")

        artifacts = list(
            db.scalars(
                select(GenerationArtifact).where(
                    GenerationArtifact.generation_job_id == job.id
                )
            ).all()
        )

        presentation = get_artifact(
            artifacts,
            "presentation",
        )

        script = get_artifact(
            artifacts,
            "script",
        )

        narration = get_artifact(
            artifacts,
            "narration",
        )

        presentation_path = storage.get_path(
            storage_key=(presentation.storage_key),
        )

        script_path = storage.get_path(
            storage_key=(script.storage_key),
        )

        narration_path = storage.get_path(
            storage_key=(narration.storage_key),
        )

    data = json.loads(
        script_path.read_text(
            encoding="utf-8",
        )
    )

    durations = [float(slide["audio_duration_seconds"]) for slide in data["slides"]]

    print()
    print(
        "Duraciones:",
        durations,
    )

    print(
        "Total slides:",
        sum(durations),
    )

    slide_dir = output_root / "slides"

    slides = render_presentation(
        presentation_path=(presentation_path),
        render_dir=slide_dir,
    )

    silent_video = output_root / "silent_video.mp4"

    build_silent_video(
        slide_images=slides,
        durations=durations,
        output_path=silent_video,
        work_dir=output_root,
    )

    final_video = output_root / "SmartVitra_rebuilt.mp4"

    mux_audio(
        silent_video_path=(silent_video),
        narration_path=(narration_path),
        output_path=final_video,
    )

    print()
    print("=" * 70)
    print("REBUILD COMPLETE")
    print("=" * 70)
    print(
        "Video:",
        final_video,
    )
    print(
        "Slides:",
        slide_dir,
    )
    print(
        "Narration source:",
        narration_path,
    )


if __name__ == "__main__":
    main()
