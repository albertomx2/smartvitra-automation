from __future__ import annotations

from dataclasses import dataclass

from backend.generation.snapshot import (
    CaseGenerationSnapshot,
    GenerationPhotoSnapshot,
    GenerationWindowSnapshot,
)


@dataclass(frozen=True)
class SolutionImageScene:
    window: GenerationWindowSnapshot
    photo: GenerationPhotoSnapshot


class SolutionImageSceneSelector:
    """
    Selects the real customer scene used by both:

    - slide 2: current/problem photograph;
    - slide 3: AI-generated proposed result.

    The rule is intentionally deterministic:
    first PrefWeb window, by position, that has both
    a customer problem and at least one real visit photo.
    """

    def select(
        self,
        snapshot: CaseGenerationSnapshot,
    ) -> SolutionImageScene | None:
        windows = sorted(
            snapshot.windows,
            key=lambda item: item.position,
        )

        for window in windows:
            if not window.problem_type:
                continue

            if not window.photos:
                continue

            return SolutionImageScene(
                window=window,
                photo=window.photos[0],
            )

        return None
