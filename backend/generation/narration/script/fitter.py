from __future__ import annotations

import re

from backend.generation.narration.script.models import (
    NarrationScript,
)


class NarrationScriptFitter:
    """
    Deterministically reduces excessively long narration while
    preserving every slide and avoiding cuts in the middle of words.

    The usual budget is 420 words. Fixed recordings and exact pricing are
    preserved; longer protected copy must still leave room for the minimum
    narration on each customer-specific slide.
    """

    TARGET_MAX_WORDS = 420
    MIN_WORDS_PER_SLIDE = 20
    FIXED_SLIDE_NUMBERS = frozenset({4, 5, 8, 9, 10})
    DETERMINISTIC_OBJECTIVES = frozenset(
        {
            "investment",
            "material_alternatives",
        }
    )

    @classmethod
    def _is_protected_slide(cls, slide) -> bool:
        """Keep fixed audio and exact deterministic prices unchanged."""

        return (
            slide.slide_number in cls.FIXED_SLIDE_NUMBERS
            or slide.commercial_objective in cls.DETERMINISTIC_OBJECTIVES
        )

    @classmethod
    def word_budget(cls, script: NarrationScript) -> int:
        required_words = sum(
            (
                len(slide.narration.split())
                if cls._is_protected_slide(slide)
                else min(len(slide.narration.split()), cls.MIN_WORDS_PER_SLIDE)
            )
            for slide in script.slides
        )
        return max(cls.TARGET_MAX_WORDS, required_words)

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
        maximum_words = self.word_budget(script)

        if total_words <= maximum_words:
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
            if self._is_protected_slide(slide)
        )

        variable_total = total_words - fixed_words
        variable_budget = maximum_words - fixed_words

        raw_targets = [
            (
                count
                if self._is_protected_slide(slide)
                else max(
                    min(count, self.MIN_WORDS_PER_SLIDE),
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
        # the budget derived from this deck's protected narration.
        while sum(raw_targets) > maximum_words:
            index = max(
                (
                    index
                    for index, slide in enumerate(script.slides)
                    if not self._is_protected_slide(slide)
                    and raw_targets[index]
                    > min(original_counts[index], self.MIN_WORDS_PER_SLIDE)
                ),
                key=lambda i: raw_targets[i],
            )

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
