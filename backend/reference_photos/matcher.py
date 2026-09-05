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


@dataclass(frozen=True)
class WindowMatchProfile:
    element_type: str
    opening_system: str | None
    leaf_configuration: str | None
    leaf_count: int | None
    has_fixed: bool


class ReferencePhotoMatcher:
    ELEMENT_WEIGHT = 40
    SYSTEM_WEIGHT = 35
    EXACT_LEAF_WEIGHT = 35
    SAME_LEAF_COUNT_WEIGHT = 22
    ADJACENT_LEAF_COUNT_WEIGHT = 10
    SAME_FIXED_WEIGHT = 5
    SYSTEM_MISMATCH_PENALTY = 25
    FIXED_ONLY_MISMATCH_PENALTY = 60
    ELEMENT_MISMATCH_PENALTY = 50
    PROBLEM_WEIGHT = 10
    WINDOW_TYPE_WEIGHT = 5
    ROOM_WEIGHT = 4
    FEATURE_WEIGHT = 1
    QUALITY_MAX = 5

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
        target = self.profile_for_window(window)

        scored: list[ScoredReferencePhoto] = []

        for photo in photos:
            score = 0

            candidate = self._candidate_profile(photo)
            score += self._structured_score(target=target, candidate=candidate)

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
            score += max(0, min(photo.quality_score, self.QUALITY_MAX))

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

    def profile_for_window(
        self,
        window: GenerationWindowSnapshot,
    ) -> WindowMatchProfile:
        target_text = " ".join(
            value
            for value in (
                window.nomenclature,
                window.reference,
                window.description,
            )
            if value
        )
        leaf_configuration = self._infer_leaf_configuration(target_text)
        return WindowMatchProfile(
            element_type=self._infer_element_type(target_text),
            opening_system=self._infer_opening_system(target_text),
            leaf_configuration=leaf_configuration,
            leaf_count=self._leaf_count(leaf_configuration),
            has_fixed=self._has_fixed(leaf_configuration, target_text),
        )

    def is_matchable_window(
        self,
        window: GenerationWindowSnapshot,
    ) -> bool:
        return self.profile_for_window(window).element_type != "accessory"

    @classmethod
    def _candidate_profile(
        cls,
        photo: ReferencePhotoCandidate,
    ) -> WindowMatchProfile:
        return WindowMatchProfile(
            element_type=photo.element_type or "window",
            opening_system=photo.opening_system,
            leaf_configuration=photo.leaf_configuration,
            leaf_count=cls._leaf_count(photo.leaf_configuration),
            has_fixed=cls._has_fixed(photo.leaf_configuration, ""),
        )

    @classmethod
    def _structured_score(
        cls,
        *,
        target: WindowMatchProfile,
        candidate: WindowMatchProfile,
    ) -> int:
        score = (
            cls.ELEMENT_WEIGHT
            if target.element_type == candidate.element_type
            else -cls.ELEMENT_MISMATCH_PENALTY
        )

        if target.opening_system and candidate.opening_system:
            if target.opening_system == candidate.opening_system:
                score += cls.SYSTEM_WEIGHT
            else:
                score -= cls.SYSTEM_MISMATCH_PENALTY

        if (
            target.opening_system != "fixed"
            and candidate.opening_system == "fixed"
            and (target.leaf_count or 0) > 0
        ):
            score -= cls.FIXED_ONLY_MISMATCH_PENALTY

        if (
            target.leaf_configuration
            and target.leaf_configuration == candidate.leaf_configuration
        ):
            score += cls.EXACT_LEAF_WEIGHT
        elif target.leaf_count is not None and candidate.leaf_count is not None:
            difference = abs(target.leaf_count - candidate.leaf_count)
            if difference == 0:
                score += cls.SAME_LEAF_COUNT_WEIGHT
            elif difference == 1:
                score += cls.ADJACENT_LEAF_COUNT_WEIGHT

        if target.has_fixed == candidate.has_fixed:
            score += cls.SAME_FIXED_WEIGHT

        return score

    @classmethod
    def _infer_element_type(cls, value: str) -> str:
        normalized = cls._normalize(value)
        if any(
            marker in normalized
            for marker in (
                "chapa alu",
                "chapa de aluminio",
                "forro",
                "embocadura",
                "peana",
                "pliegue",
            )
        ):
            return "accessory"
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
        if re.search(r"\bfij[oa]\b", normalized) and "hoja" not in normalized:
            return "fixed"
        if "openmax" in normalized:
            return "openmax"
        if "ventana" in normalized and "hoja" in normalized:
            return "tilt_turn"
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

    @staticmethod
    def _leaf_count(configuration: str | None) -> int | None:
        return {
            "one_leaf": 1,
            "leaf_plus_fixed": 1,
            "two_leaves": 2,
            "two_leaves_plus_fixed": 2,
            "three_leaves": 3,
            "four_leaves": 4,
        }.get(configuration or "")

    @classmethod
    def _has_fixed(
        cls,
        configuration: str | None,
        raw_text: str,
    ) -> bool:
        return configuration in {
            "leaf_plus_fixed",
            "two_leaves_plus_fixed",
        } or "fijo" in cls._normalize(raw_text)

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
