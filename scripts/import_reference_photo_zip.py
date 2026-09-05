from __future__ import annotations

import argparse
import hashlib
import io
import mimetypes
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from sqlalchemy import select

from backend.db.models.reference_photo import ReferencePhoto
from backend.db.session import SessionLocal
from backend.storage.reference import ReferencePhotoStorage

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass(frozen=True)
class Classification:
    element_type: str
    opening_system: str | None
    leaf_configuration: str | None
    description: str
    window_type_tags: list[str]


def _normalized(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFD", value.upper())
        if unicodedata.category(character) != "Mn"
    )


def classify(source_path: str) -> Classification | None:
    parts = [_normalized(part) for part in Path(source_path).parts]
    joined = "/".join(parts)
    if "00_PENDIENTE_CLASIFICAR" in joined or "__MACOSX" in joined:
        return None

    element_mappings = (
        ("01_VENTANAS", "window", "ventana"),
        ("02_BALCONERAS", "balcony_door", "balconera o puerta"),
        ("03_CERRAMIENTOS", "special_enclosure", "cerramiento especial"),
        ("04_MIRADORES", "special_enclosure", "mirador"),
        ("05_ENTRADAS", "entrance", "entrada"),
        ("06_PORTONES", "gate", "portón"),
        ("07_NUDO FRANCES", "french_joint", "nudo francés"),
        ("08_ESTORES", "blind", "estor"),
        ("09_CORTINAS", "curtain", "cortina"),
    )
    element = next(
        ((code, label) for marker, code, label in element_mappings if marker in joined),
        None,
    )
    if element is None:
        return None

    system_mappings = (
        ("CORREDERA_PARALELA", "parallel_sliding", "corredera paralela"),
        ("CORREDERA_ELEVABLE", "lift_slide", "corredera elevable"),
        ("ABATIBLE_OSCILOBATIENTE", "tilt_turn", "abatible/oscilobatiente"),
        ("/CORREDERA/", "sliding", "corredera"),
        ("/FIJO/", "fixed", "fijo"),
        ("/OPENMAX", "openmax", "OpenMax"),
    )
    system = next(
        ((code, label) for marker, code, label in system_mappings if marker in joined),
        None,
    )

    leaf_mappings = (
        ("2_HOJAS_MAS_FIJO", "two_leaves_plus_fixed", "2 hojas más fijo"),
        ("1_HOJA_MAS_FIJO", "leaf_plus_fixed", "1 hoja más fijo"),
        ("HOJA_MAS_FIJO", "leaf_plus_fixed", "1 hoja más fijo"),
        ("4_HOJAS", "four_leaves", "4 hojas"),
        ("3_HOJAS", "three_leaves", "3 hojas"),
        ("2_HOJAS", "two_leaves", "2 hojas"),
        ("1_HOJA", "one_leaf", "1 hoja"),
    )
    leaf = next(
        ((code, label) for marker, code, label in leaf_mappings if marker in joined),
        None,
    )

    element_code, element_label = element
    system_code, system_label = system or (None, None)
    leaf_code, leaf_label = leaf or (None, None)
    labels = [element_label, system_label, leaf_label]
    description = "Trabajo realizado: " + ", ".join(label for label in labels if label)
    tags = [label for label in (system_label, leaf_label, element_label) if label]
    return Classification(
        element_type=element_code,
        opening_system=system_code,
        leaf_configuration=leaf_code,
        description=description,
        window_type_tags=tags,
    )


def quality_score(width: int, height: int) -> int:
    shortest = min(width, height)
    megapixels = width * height / 1_000_000
    return min(
        10,
        (5 if shortest >= 720 else 3 if shortest >= 500 else 1)
        + (3 if megapixels >= 2 else 2 if megapixels >= 1 else 1)
        + (2 if height >= width else 1),
    )


def import_zip(zip_path: Path) -> tuple[int, int, int]:
    storage = ReferencePhotoStorage()
    imported = skipped = duplicates = 0
    seen_hashes: set[str] = set()

    with SessionLocal() as db, zipfile.ZipFile(zip_path) as archive:
        existing_hashes = set(
            db.scalars(
                select(ReferencePhoto.content_sha256).where(
                    ReferencePhoto.content_sha256.is_not(None)
                )
            ).all()
        )

        for member in sorted(archive.infolist(), key=lambda item: item.filename):
            if (
                member.is_dir()
                or Path(member.filename).suffix.lower() not in IMAGE_EXTENSIONS
            ):
                continue
            classification = classify(member.filename)
            if classification is None:
                skipped += 1
                continue

            content = archive.read(member)
            digest = hashlib.sha256(content).hexdigest()
            if digest in seen_hashes or digest in existing_hashes:
                duplicates += 1
                continue

            with Image.open(io.BytesIO(content)) as image:
                image.verify()
            with Image.open(io.BytesIO(content)) as image:
                width, height = image.size

            storage_key = storage.save(
                filename=Path(member.filename).name,
                content=content,
            )
            try:
                db.add(
                    ReferencePhoto(
                        original_filename=Path(member.filename).name,
                        storage_key=storage_key,
                        content_type=(
                            mimetypes.guess_type(member.filename)[0] or "image/jpeg"
                        ),
                        description=classification.description,
                        problem_tags=[],
                        room_tags=[],
                        window_type_tags=classification.window_type_tags,
                        feature_tags=[],
                        element_type=classification.element_type,
                        opening_system=classification.opening_system,
                        leaf_configuration=classification.leaf_configuration,
                        content_sha256=digest,
                        source_path=member.filename,
                        width_px=width,
                        height_px=height,
                        quality_score=quality_score(width, height),
                        active=True,
                    )
                )
                db.commit()
            except Exception:
                db.rollback()
                storage.delete(storage_key=storage_key)
                raise

            seen_hashes.add(digest)
            imported += 1

    return imported, skipped, duplicates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path", type=Path)
    args = parser.parse_args()
    imported, skipped, duplicates = import_zip(args.zip_path)
    print(f"imported={imported} skipped={skipped} duplicates={duplicates}")


if __name__ == "__main__":
    main()
