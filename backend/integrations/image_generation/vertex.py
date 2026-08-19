from __future__ import annotations

import mimetypes
import os
from pathlib import Path

from google import genai
from google.genai import types


class VertexSolutionImageClient:
    DEFAULT_MODEL = "gemini-2.5-flash-image"

    def __init__(
        self,
        *,
        project_id: str | None = None,
        location: str | None = None,
        model: str | None = None,
    ) -> None:
        resolved_project = project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or ""

        if not resolved_project:
            raise ValueError("GOOGLE_CLOUD_PROJECT is required")

        resolved_location = location or os.getenv("GOOGLE_CLOUD_LOCATION") or "global"

        self._client = genai.Client(
            vertexai=True,
            project=resolved_project,
            location=resolved_location,
        )

        self._model = model or os.getenv("SOLUTION_IMAGE_MODEL") or self.DEFAULT_MODEL

    def generate(
        self,
        *,
        source_photo: Path,
        window_reference: Path,
        prompt: str,
        output_path: Path,
    ) -> Path:
        source_part = self._image_part(
            source_photo,
        )

        reference_part = self._image_part(
            window_reference,
        )

        content = types.Content(
            role="user",
            parts=[
                source_part,
                reference_part,
                types.Part.from_text(
                    text=prompt,
                ),
            ],
        )

        response = self._client.models.generate_content(
            model=self._model,
            contents=content,
            config=types.GenerateContentConfig(
                response_modalities=[
                    types.Modality.TEXT,
                    types.Modality.IMAGE,
                ],
                candidate_count=1,
                temperature=0.2,
            ),
        )

        image_bytes: bytes | None = None

        for candidate in response.candidates or []:
            candidate_content = candidate.content

            if candidate_content is None:
                continue

            for part in candidate_content.parts or []:
                inline_data = part.inline_data

                if inline_data is not None and inline_data.data:
                    image_bytes = inline_data.data
                    break

            if image_bytes is not None:
                break

        if image_bytes is None:
            raise RuntimeError("Vertex AI returned no generated image")

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_bytes(
            image_bytes,
        )

        if output_path.stat().st_size == 0:
            raise RuntimeError("Vertex AI generated an empty image")

        return output_path

    @staticmethod
    def _image_part(
        path: Path,
    ) -> types.Part:
        if not path.exists():
            raise FileNotFoundError(
                path,
            )

        mime_type, _ = mimetypes.guess_type(
            path.name,
        )

        if mime_type not in {
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/heic",
            "image/heif",
        }:
            raise ValueError(
                "Unsupported source image type " f"for Vertex AI: {mime_type}"
            )

        return types.Part.from_bytes(
            data=path.read_bytes(),
            mime_type=mime_type,
        )
