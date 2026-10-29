from __future__ import annotations

import re
import unicodedata
from enum import StrEnum
from pathlib import Path
from typing import ClassVar

from backend.generation.snapshot import CaseGenerationSnapshot


class HomeProblem(StrEnum):
    NOISE = "noise"
    HEAT = "heat"
    COLD = "cold"


class ProblemSlideSelector:
    ASSET_DIR = Path("assets/presentation/problem_variants")

    _ASSETS: ClassVar[dict[frozenset[HomeProblem], str]] = {
        frozenset({HomeProblem.NOISE, HomeProblem.HEAT, HomeProblem.COLD}): (
            "noise_heat_cold.png"
        ),
        frozenset({HomeProblem.HEAT, HomeProblem.NOISE}): "heat_noise.png",
        frozenset({HomeProblem.COLD, HomeProblem.NOISE}): "cold_noise.png",
        frozenset({HomeProblem.COLD, HomeProblem.HEAT}): "cold_heat.png",
        frozenset({HomeProblem.NOISE}): "noise.png",
        frozenset({HomeProblem.HEAT}): "heat.png",
        frozenset({HomeProblem.COLD}): "cold.png",
    }

    _NOISE_PATTERNS = (
        r"\bruido(?:s)?\b",
        r"\bacustic[ao]s?\b",
        r"\btrafico\b",
        r"\bsonor[ao]s?\b",
    )
    _HEAT_PATTERNS = (
        r"\bcalor\b",
        r"\bcaluros[ao]s?\b",
        r"\bverano\b",
        r"\bsobrecalentamiento\b",
        r"\bproteccion solar\b",
        r"\bexceso de sol\b",
        r"\btemperaturas? altas?\b",
    )
    _COLD_PATTERNS = (
        r"\bfrio\b",
        r"\binvierno\b",
        r"\bcorrientes? de aire\b",
        r"\bentra(?:da)? de aire\b",
        r"\binfiltraciones?\b",
        r"\bperdida de calor\b",
        r"\btemperaturas? bajas?\b",
    )
    _THERMAL_PATTERNS = (
        r"\btermic[ao]s?\b",
        r"\btemperatura\b",
    )

    def select(self, snapshot: CaseGenerationSnapshot) -> Path:
        problems = self.detect(snapshot)
        filename = self._ASSETS[problems]
        path = self.ASSET_DIR / filename

        if not path.exists():
            raise FileNotFoundError(path)

        return path

    def detect(self, snapshot: CaseGenerationSnapshot) -> frozenset[HomeProblem]:
        problems: set[HomeProblem] = set()
        thermal_is_selected = False

        texts = [snapshot.visit_notes or ""]

        for window in snapshot.windows:
            texts.append(window.commercial_notes or "")
            problem_type = self._normalize(window.problem_type or "")

            if problem_type == "noise":
                problems.add(HomeProblem.NOISE)
            elif problem_type == "air":
                problems.add(HomeProblem.COLD)
            elif problem_type == "thermal":
                thermal_is_selected = True

        normalized_text = " ".join(self._normalize(value) for value in texts)

        if self._matches(normalized_text, self._NOISE_PATTERNS):
            problems.add(HomeProblem.NOISE)
        if self._matches(normalized_text, self._HEAT_PATTERNS):
            problems.add(HomeProblem.HEAT)
        if self._matches(normalized_text, self._COLD_PATTERNS):
            problems.add(HomeProblem.COLD)

        thermal_is_reported = self._matches(
            normalized_text,
            self._THERMAL_PATTERNS,
        )

        if (thermal_is_selected or thermal_is_reported) and not problems.intersection(
            {HomeProblem.HEAT, HomeProblem.COLD}
        ):
            problems.update({HomeProblem.HEAT, HomeProblem.COLD})

        if not problems:
            # A case can be generated before the commercial fills in the
            # problem fields. Use the neutral all-year comfort slide rather
            # than inventing an acoustic problem.
            problems.update({HomeProblem.HEAT, HomeProblem.COLD})

        return frozenset(problems)

    @staticmethod
    def _matches(value: str, patterns: tuple[str, ...]) -> bool:
        return any(re.search(pattern, value) is not None for pattern in patterns)

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value)
        without_accents = "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        )
        return " ".join(without_accents.lower().split())
