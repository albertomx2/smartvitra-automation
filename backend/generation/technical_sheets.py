from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path

from backend.generation.snapshot import CaseGenerationSnapshot
from backend.reference_photos.matcher import ReferencePhotoMatcher


@dataclass(frozen=True)
class TechnicalSheet:
    filename: str
    path: Path


class TechnicalSheetSelector:
    ASSET_DIR = Path("assets/technical")

    THERMOACUSTIC = TechnicalSheet(
        filename="Ficha tecnica Cajon SUMUM Thermoacustic.pdf",
        path=ASSET_DIR / "SUMUM Ficha Cajón SUMUM Thermoacustic.pdf",
    )
    MICROVENTILATION = TechnicalSheet(
        filename="Ficha tecnica Microventilacion.pdf",
        path=ASSET_DIR / "SUMUM Ficha tecnica Microventilación.pdf",
    )
    UNIK = TechnicalSheet(
        filename="Ficha tecnica UNIK.pdf",
        path=ASSET_DIR / "SUMUM Ficha técnica UNIK.pdf",
    )
    ISLIDE = TechnicalSheet(
        filename="Ficha tecnica iSlide.pdf",
        path=ASSET_DIR / "SUMUM Ficha tecnica Islide.pdf",
    )

    def select(self, snapshot: CaseGenerationSnapshot) -> list[TechnicalSheet]:
        selected: list[TechnicalSheet] = []

        all_text = " ".join(
            filter(
                None,
                (
                    *(
                        value
                        for window in snapshot.windows
                        for value in (
                            window.nomenclature,
                            window.reference,
                            window.description,
                            window.room,
                            window.commercial_notes,
                        )
                    ),
                    *(
                        value
                        for item in snapshot.items
                        for value in (
                            item.nomenclature,
                            item.reference,
                            item.description,
                            item.internal_remarks,
                            item.item_type,
                            item.item_subtype,
                        )
                    ),
                ),
            )
        )
        normalized = self._normalize(all_text)

        if "persian" in normalized:
            selected.append(self.THERMOACUSTIC)

        opening_systems = {
            ReferencePhotoMatcher._infer_opening_system(
                " ".join(
                    filter(
                        None,
                        (
                            window.nomenclature,
                            window.reference,
                            window.description,
                            window.room,
                        ),
                    )
                )
            )
            for window in snapshot.windows
        }

        if "tilt_turn" in opening_systems:
            selected.extend(
                (
                    self.MICROVENTILATION,
                    self.UNIK,
                )
            )

        if "sliding" in opening_systems:
            selected.append(self.ISLIDE)

        for sheet in selected:
            if not sheet.path.is_file():
                raise FileNotFoundError(f"Technical sheet is missing: {sheet.path}")

        return selected

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value)
        return "".join(
            character
            for character in decomposed.casefold()
            if not unicodedata.combining(character)
        )
