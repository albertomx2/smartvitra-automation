from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from backend.generation.snapshot import (
    GenerationWindowSnapshot,
)


@dataclass(frozen=True)
class ReferencePhotoCandidate:
    id: str

    problem_tags: list[str]
    room_tags: list[str]
    window_type_tags: list[str]
    feature_tags: list[str]
    element_type: str | None = None
    opening_system: str | None = None
    leaf_configuration: str | None = None
    quality_score: int = 0


@dataclass(frozen=True)
class ScoredReferencePhoto:
    photo: ReferencePhotoCandidate
    score: int


class ReferencePhotoMatcher:
    ELEMENT_WEIGHT = 50
    SYSTEM_WEIGHT = 40
    LEAF_WEIGHT = 30
    PROBLEM_WEIGHT = 10
    WINDOW_TYPE_WEIGHT = 5
    ROOM_WEIGHT = 4
    FEATURE_WEIGHT = 1

    def rank_for_window(
        self,
        *,
        window: GenerationWindowSnapshot,
        photos: list[ReferencePhotoCandidate],
    ) -> list[ScoredReferencePhoto]:
        problem = self._normalize(window.problem_type) if window.problem_type else None

        room_tokens = self._room_tokens(window.room)

        window_tokens = self._tokens(window.description or "")

        feature_tokens = self._tokens(window.color or "")
        target_text = " ".join(
            value
            for value in (
                window.nomenclature,
                window.reference,
                window.description,
            )
            if value
        )
        target_element = self._infer_element_type(target_text)
        target_system = self._infer_opening_system(target_text)
        target_leaf = self._infer_leaf_configuration(target_text)

        scored: list[ScoredReferencePhoto] = []

        for photo in photos:
            score = 0

            if photo.element_type and photo.element_type == target_element:
                score += self.ELEMENT_WEIGHT

            if target_system and photo.opening_system == target_system:
                score += self.SYSTEM_WEIGHT

            if target_leaf and photo.leaf_configuration == target_leaf:
                score += self.LEAF_WEIGHT

            problems = {self._normalize(value) for value in photo.problem_tags}

            rooms: set[str] = set()

            for value in photo.room_tags:
                rooms.update(self._room_tokens(value))

            photo_window_tokens: set[str] = set()

            for value in photo.window_type_tags:
                photo_window_tokens.update(self._tokens(value))

            photo_feature_tokens: set[str] = set()

            for value in photo.feature_tags:
                photo_feature_tokens.update(self._tokens(value))

            if problem and problem in problems:
                score += self.PROBLEM_WEIGHT

            score += len(room_tokens & rooms) * self.ROOM_WEIGHT

            score += len(window_tokens & photo_window_tokens) * self.WINDOW_TYPE_WEIGHT

            score += len(feature_tokens & photo_feature_tokens) * self.FEATURE_WEIGHT
            score += max(0, min(photo.quality_score, 10))

            scored.append(
                ScoredReferencePhoto(
                    photo=photo,
                    score=score,
                )
            )

        return sorted(
            scored,
            key=lambda item: (
                item.score,
                item.photo.id,
            ),
            reverse=True,
        )

    @classmethod
    def _infer_element_type(cls, value: str) -> str:
        normalized = cls._normalize(value)
        if "balconera" in normalized or "puerta" in normalized:
            return "balcony_door"
        if "cerramiento" in normalized or "mirador" in normalized:
            return "special_enclosure"
        return "window"

    @classmethod
    def _infer_opening_system(cls, value: str) -> str | None:
        normalized = cls._normalize(value)
        if "paralela" in normalized:
            return "parallel_sliding"
        if "elevable" in normalized:
            return "lift_slide"
        if "corredera" in normalized or "islide" in normalized:
            return "sliding"
        if "oscilobat" in normalized or "abatible" in normalized:
            return "tilt_turn"
        if re.search(r"\bfij[oa]\b", normalized):
            return "fixed"
        if "openmax" in normalized:
            return "openmax"
        return None

    @classmethod
    def _infer_leaf_configuration(cls, value: str) -> str | None:
        normalized = cls._normalize(value)
        fixed = "fijo" in normalized
        mappings = (
            (r"\b(?:4|cuatro)\s*hojas?\b", "four_leaves"),
            (r"\b(?:3|tres)\s*hojas?\b", "three_leaves"),
            (
                r"\b(?:2|dos)\s*hojas?\b",
                "two_leaves_plus_fixed" if fixed else "two_leaves",
            ),
            (r"\b(?:1|una?)\s*hojas?\b", "leaf_plus_fixed" if fixed else "one_leaf"),
        )
        for pattern, classification in mappings:
            if re.search(pattern, normalized):
                return classification
        if fixed and "hoja" in normalized:
            return "leaf_plus_fixed"
        return None

    @classmethod
    def _room_tokens(
        cls,
        value: str | None,
    ) -> set[str]:
        if not value:
            return set()

        normalized = cls._normalize(value)

        result = {
            normalized,
        }

        if "hab" in normalized or "dorm" in normalized:
            result.update(
                {
                    "habitacion",
                    "dormitorio",
                }
            )

        if "salon" in normalized:
            result.add("salon")

        if "cocina" in normalized:
            result.add("cocina")

        if "bano" in normalized:
            result.add("bano")

        return result

    @classmethod
    def _tokens(
        cls,
        value: str,
    ) -> set[str]:
        normalized = cls._normalize(value)

        return {
            token
            for token in re.split(
                r"[^a-z0-9]+",
                normalized,
            )
            if len(token) >= 3
        }

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        value = value.strip().lower()

        value = "".join(
            character
            for character in unicodedata.normalize(
                "NFD",
                value,
            )
            if (unicodedata.category(character) != "Mn")
        )

        return value
