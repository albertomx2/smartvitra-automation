from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from backend.generation.video.font_normalizer import (
    normalize_pptx_fonts,
)


class NarratedPresentationVideoRenderer:
    SLIDE_COUNT = 9

    def render(
        self,
        *,
        presentation_path: Path,
        slide_audio_paths: list[Path],
        output_video_path: Path,
        output_audio_path: Path,
        work_dir: Path,
    ) -> Path:
        if len(slide_audio_paths) != self.SLIDE_COUNT:
            raise ValueError("Exactly 9 slide audio files " "are required")

        for binary in (
            "libreoffice",
            "pdftoppm",
            "ffmpeg",
            "ffprobe",
        ):
            self._require_binary(
                binary,
            )

        render_dir = work_dir / "video_render"

        render_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # IMPORTANT:
        # The downloadable PPTX is left untouched.
        #
        # Only the temporary copy used by
        # LibreOffice is normalized for Linux.
        normalized_presentation = render_dir / "presentation_for_video.pptx"

        normalize_pptx_fonts(
            source_path=presentation_path,
            output_path=(normalized_presentation),
        )

        pdf_path = self._render_pdf(
            presentation_path=(normalized_presentation),
            render_dir=render_dir,
        )

        slide_images = self._render_slide_images(
            pdf_path=pdf_path,
            render_dir=render_dir,
        )

        if len(slide_images) < self.SLIDE_COUNT:
            raise RuntimeError(
                "Rendered presentation has "
                f"{len(slide_images)} slides; "
                "expected at least "
                f"{self.SLIDE_COUNT}"
            )

        durations = [
            self.probe_duration(
                path=audio_path,
            )
            for audio_path in slide_audio_paths
        ]

        silent_video_path = render_dir / "silent_video.mp4"

        self._build_silent_video(
            slide_images=(slide_images[: self.SLIDE_COUNT]),
            durations=durations,
            output_path=(silent_video_path),
            render_dir=render_dir,
        )

        # Build ONE continuous narration file.
        #
        # This avoids AAC/MP4 discontinuities
        # at slide boundaries.
        self._concatenate_audio(
            slide_audio_paths=(slide_audio_paths),
            output_path=(output_audio_path),
            render_dir=render_dir,
        )

        self._mux_audio(
            silent_video_path=(silent_video_path),
            narration_path=(output_audio_path),
            output_path=(output_video_path),
        )

        return output_video_path

    @staticmethod
    def probe_duration(
        *,
        path: Path,
    ) -> float:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                ("default=" "noprint_wrappers=1:" "nokey=1"),
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        return float(result.stdout.strip())

    @staticmethod
    def _require_binary(
        name: str,
    ) -> None:
        if shutil.which(name) is None:
            raise RuntimeError("Required executable " f"{name!r} is not installed")

    @staticmethod
    def _render_pdf(
        *,
        presentation_path: Path,
        render_dir: Path,
    ) -> Path:
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(render_dir),
                str(presentation_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )

        pdf_path = render_dir / (presentation_path.stem + ".pdf")

        if not pdf_path.exists():
            raise RuntimeError("LibreOffice did not " "create the PDF")

        return pdf_path

    @staticmethod
    def _render_slide_images(
        *,
        pdf_path: Path,
        render_dir: Path,
    ) -> list[Path]:
        prefix = render_dir / "slide"

        subprocess.run(
            [
                "pdftoppm",
                "-png",
                "-r",
                "180",
                str(pdf_path),
                str(prefix),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )

        paths = list(render_dir.glob("slide-*.png"))

        def number(
            path: Path,
        ) -> int:
            return int(path.stem.split("-")[-1])

        return sorted(
            paths,
            key=number,
        )

    @staticmethod
    def _build_silent_video(
        *,
        slide_images: list[Path],
        durations: list[float],
        output_path: Path,
        render_dir: Path,
    ) -> None:
        if len(slide_images) != len(durations):
            raise ValueError("Slide image and duration " "counts differ")

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
            segment_path = render_dir / (f"silent_" f"{index:02d}.mp4")

            subprocess.run(
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
                        "force_original_"
                        "aspect_ratio=decrease,"
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
                    str(segment_path),
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
            )

            segments.append(segment_path)

        NarratedPresentationVideoRenderer._concat_video_segments(
            segment_paths=segments,
            output_path=output_path,
            render_dir=render_dir,
        )

    @staticmethod
    def _concat_video_segments(
        *,
        segment_paths: list[Path],
        output_path: Path,
        render_dir: Path,
    ) -> None:
        concat_path = render_dir / "silent_segments.txt"

        concat_path.write_text(
            "\n".join(
                (
                    "file '"
                    + str(path.resolve()).replace(
                        "'",
                        "'\\''",
                    )
                    + "'"
                )
                for path in segment_paths
            ),
            encoding="utf-8",
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-c",
                "copy",
                str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )

    @staticmethod
    def _concatenate_audio(
        *,
        slide_audio_paths: list[Path],
        output_path: Path,
        render_dir: Path,
    ) -> None:
        concat_path = render_dir / "audio_segments.txt"

        concat_path.write_text(
            "\n".join(
                (
                    "file '"
                    + str(path.resolve()).replace(
                        "'",
                        "'\\''",
                    )
                    + "'"
                )
                for path in slide_audio_paths
            ),
            encoding="utf-8",
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-vn",
                "-c:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )

    @staticmethod
    def _mux_audio(
        *,
        silent_video_path: Path,
        narration_path: Path,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        subprocess.run(
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
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
        )
