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


@dataclass(frozen=True)
class ScoredReferencePhoto:
    photo: ReferencePhotoCandidate
    score: int


class ReferencePhotoMatcher:
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

        scored: list[ScoredReferencePhoto] = []

        for photo in photos:
            score = 0

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
