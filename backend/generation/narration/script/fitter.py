from __future__ import annotations

import re

from backend.generation.narration.script.models import (
    NarrationScript,
)


class NarrationScriptFitter:
    """
    Deterministically reduces excessively long narration while
    preserving every slide and avoiding cuts in the middle of words.

    420 words gives a safety margin below both:
    - validator MAX_WORDS = 430
    - validator MAX_DURATION_SECONDS = 190 at 135 wpm
    """

    TARGET_MAX_WORDS = 420
    MIN_WORDS_PER_SLIDE = 20
    FIXED_SLIDE_NUMBERS = frozenset({4, 5, 6, 8, 9})

    @staticmethod
    def _word_count(
        value: str,
    ) -> int:
        return len(value.split())

    @staticmethod
    def _fit_text(
        value: str,
        maximum_words: int,
    ) -> str:
        cleaned = " ".join(value.split())

        words = cleaned.split()

        if len(words) <= maximum_words:
            return cleaned

        # Prefer keeping complete sentences.
        sentences = re.split(
            r"(?<=[.!?])\s+",
            cleaned,
        )

        selected: list[str] = []
        current_words = 0

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            sentence_words = len(sentence.split())

            if current_words + sentence_words > maximum_words:
                break

            selected.append(sentence)
            current_words += sentence_words

        # If complete-sentence fitting retained enough content,
        # use it directly.
        minimum_reasonable = max(
            8,
            int(maximum_words * 0.65),
        )

        if selected and current_words >= minimum_reasonable:
            result = " ".join(selected).strip()

            if result[-1] not in ".!?":
                result += "."

            return result

        # Fallback: cut only at a word boundary.
        shortened = " ".join(words[:maximum_words]).rstrip(" ,;:-")

        # Avoid dangling connectors.
        incomplete_endings = {
            "a",
            "al",
            "con",
            "de",
            "del",
            "e",
            "el",
            "en",
            "la",
            "las",
            "los",
            "o",
            "para",
            "por",
            "que",
            "sin",
            "u",
            "un",
            "una",
            "y",
        }

        fitted_words = shortened.split()

        while (
            fitted_words
            and fitted_words[-1].strip(".,;:!?").lower() in incomplete_endings
        ):
            fitted_words.pop()

        shortened = " ".join(fitted_words).rstrip(" ,;:-")

        if shortened and shortened[-1] not in ".!?":
            shortened += "."

        return shortened

    def fit(
        self,
        script: NarrationScript,
    ) -> NarrationScript:
        total_words = sum(self._word_count(slide.narration) for slide in script.slides)

        if total_words <= self.TARGET_MAX_WORDS:
            return script

        # Fixed slides have pre-generated audio. Their text must never change,
        # otherwise the persisted MP3 would no longer match the script.
        original_counts = [self._word_count(slide.narration) for slide in script.slides]

        fixed_words = sum(
            count
            for slide, count in zip(
                script.slides,
                original_counts,
                strict=True,
            )
            if slide.slide_number in self.FIXED_SLIDE_NUMBERS
        )

        variable_total = total_words - fixed_words
        variable_budget = self.TARGET_MAX_WORDS - fixed_words

        raw_targets = [
            (
                count
                if slide.slide_number in self.FIXED_SLIDE_NUMBERS
                else max(
                    self.MIN_WORDS_PER_SLIDE,
                    int(count / variable_total * variable_budget),
                )
            )
            for slide, count in zip(
                script.slides,
                original_counts,
                strict=True,
            )
        ]

        # Correct rounding/floor effects so the sum never exceeds
        # TARGET_MAX_WORDS.
        while sum(raw_targets) > self.TARGET_MAX_WORDS:
            index = max(
                (
                    index
                    for index, slide in enumerate(script.slides)
                    if slide.slide_number not in self.FIXED_SLIDE_NUMBERS
                ),
                key=lambda i: raw_targets[i],
            )

            if raw_targets[index] <= self.MIN_WORDS_PER_SLIDE:
                break

            raw_targets[index] -= 1

        fitted_slides = []

        for slide, target in zip(
            script.slides,
            raw_targets,
            strict=True,
        ):
            narration = self._fit_text(
                slide.narration,
                target,
            )

            fitted_slides.append(
                slide.model_copy(
                    update={
                        "narration": narration,
                    }
                )
            )

        return script.model_copy(
            update={
                "slides": fitted_slides,
            }
        )
