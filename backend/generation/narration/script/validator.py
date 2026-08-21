from __future__ import annotations

from typing import ClassVar

from backend.generation.narration.script.models import (
    NarrationScript,
)


class NarrationScriptValidationError(
    ValueError,
):
    pass


class NarrationScriptValidator:
    MIN_WORDS = 280
    MAX_WORDS = 430

    MIN_DURATION_SECONDS = 120
    MAX_DURATION_SECONDS = 190

    EXPECTED_SLIDES: ClassVar[list[int]] = list(range(1, 10))

    def validate(
        self,
        script: NarrationScript,
    ) -> None:
        numbers = [slide.slide_number for slide in script.slides]

        if numbers != self.EXPECTED_SLIDES:
            raise NarrationScriptValidationError(
                "Narration must contain slides " "1 through 9 in order"
            )

        actual_words = len(script.full_text.split())

        if actual_words < self.MIN_WORDS:
            raise NarrationScriptValidationError(
                "Narration is too short: " f"{actual_words} words"
            )

        if actual_words > self.MAX_WORDS:
            raise NarrationScriptValidationError(
                "Narration is too long: " f"{actual_words} words"
            )

        if script.estimated_duration_seconds < self.MIN_DURATION_SECONDS:
            raise NarrationScriptValidationError(
                "Estimated narration duration " "is too short"
            )

        if script.estimated_duration_seconds > self.MAX_DURATION_SECONDS:
            raise NarrationScriptValidationError(
                "Estimated narration duration " "is too long"
            )
