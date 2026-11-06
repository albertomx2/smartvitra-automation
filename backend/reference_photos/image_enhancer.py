from __future__ import annotations

import hashlib
import os
from pathlib import Path
from uuid import uuid4

from PIL import Image

from backend.integrations.image_generation.vertex import VertexSolutionImageClient
from backend.rendering.pptx.image_normalizer import PptxImageNormalizer
from backend.storage.r2 import R2StorageClient

RELATED_PROJECT_PROMPT = """
Create the finished AFTER version of this real window-installation photo.
Mandatory edits, in this order:
1. REMOVE every paper label, manufacturer sticker and document from the glass.
   REMOVE temporary ceiling brackets, exposed fixings, tape and protective film.
2. COMPLETE any unfinished building work. Repair and paint the surrounding
   walls and ceiling, finish all trim and flooring and clear all rubble and tools.
3. ADD one realistic adult person relaxing or reading beside the window.
4. Make the room welcoming with soft natural daylight and restrained decoration.

These edits take priority over copying incidental details from the source.
Never carry installation labels or unfinished work into the final image.
Produce a polished, photorealistic architectural lifestyle photograph of the SAME place.

Preserve the actual windows: their location, proportions, frame colour,
number of leaves, mullions, glazing and opening system. Keep the architecture,
perspective and recognizable identity of the original installation. Do not
invent a different window, add windows or change the structural opening.

If the room or facade is under construction, visualize the work fully finished:
complete plaster and paint around the installation, clean the floor and remove
rubble, tools, protective plastic, exposed foam, dust and temporary materials.
Remove all manufacturer labels and installation stickers from the glass,
paperwork taped to panes, masking tape and unused temporary ceiling brackets
or hanging installation fixings. Leave clean, unobstructed glass and fully
finished painted walls and ceiling. Keep the actual window handles and hardware.
Use restrained, realistic decoration and pleasant natural light. The result
must look professionally finished, welcoming and lived-in, never like a worksite.

Include one natural-looking adult person at a believable scale, relaxing or
reading near the window. Keep the person secondary and avoid covering the
window frames or glass. For an exterior scene, place the person naturally
beside the facade without blocking the installation. Use realistic anatomy,
hands, reflections, shadows and consistent lighting.

Deliver a single vertical 3:4 photograph, filling the whole frame. Keep the
entire window installation visible. No collage, split screen, borders, text,
watermarks or logos. This is an illustrative recreation based on the real photo.
""".strip()


class RelatedProjectImageEnhancer:
    """Create one reusable illustration without changing the source library."""

    def __init__(self, *, cache_root: Path | None = None) -> None:
        self._root = cache_root or Path("var/reference_photo_renders")
        self._backend = (os.getenv("STORAGE_BACKEND") or "local").lower()
        if self._backend not in {"local", "r2"}:
            raise RuntimeError(f"Unsupported STORAGE_BACKEND: {self._backend}")
        self._model = (
            os.getenv("RELATED_PROJECT_IMAGE_MODEL") or "gemini-3.1-flash-image"
        )
        self._r2 = R2StorageClient() if self._backend == "r2" else None

    def enhance(self, *, source_photo: Path) -> Path:
        digest = hashlib.sha256()
        digest.update(source_photo.read_bytes())
        digest.update(RELATED_PROJECT_PROMPT.encode())
        digest.update(self._model.encode())
        digest.update(b"portrait-3:4-v1")
        filename = f"{digest.hexdigest()}.png"
        output_path = self._root / filename
        remote_key = f"reference_photo_renders/{filename}"

        if self._valid_image(output_path):
            return output_path

        if self._r2 is not None and self._r2.exists(storage_key=remote_key):
            self._r2.download_file(storage_key=remote_key, destination=output_path)
            if self._valid_image(output_path):
                return output_path

        self._root.mkdir(parents=True, exist_ok=True)
        upright = PptxImageNormalizer().normalize(
            image_path=source_photo,
            work_dir=self._root / "upright_sources",
        )
        temporary = self._root / f"{digest.hexdigest()}-{uuid4().hex}.generated.png"
        VertexSolutionImageClient(model=self._model).generate(
            source_photo=upright,
            prompt=RELATED_PROJECT_PROMPT,
            output_path=temporary,
            aspect_ratio="3:4",
        )
        if not self._valid_image(temporary):
            raise RuntimeError("Gemini returned an invalid related-project image")

        # Encode the validated response as PNG, even if Vertex returned JPEG.
        with Image.open(temporary) as generated:
            converted = generated.convert("RGB")
        converted.save(temporary, format="PNG")
        temporary.replace(output_path)

        if self._r2 is not None:
            self._r2.upload_file(
                storage_key=remote_key,
                path=output_path,
                content_type="image/png",
            )
        return output_path

    @staticmethod
    def _valid_image(path: Path) -> bool:
        if not path.is_file():
            return False
        try:
            with Image.open(path) as image:
                image.verify()
            return True
        except (OSError, ValueError):
            return False
