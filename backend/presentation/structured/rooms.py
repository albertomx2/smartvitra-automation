from collections import Counter

from backend.commercial.models import (
    BriefOpening,
)
from backend.presentation.structured.models import (
    RoomsTableContent,
    RoomWindowSummary,
)

MAX_VISIBLE_ROOM_GROUPS = 3


def build_rooms_table(
    openings: list[BriefOpening],
) -> RoomsTableContent:
    counts: Counter[str] = Counter()

    for opening in openings:
        room = opening.room.strip() if opening.room else "Sin especificar"

        counts[room] += 1

    ordered = sorted(
        counts.items(),
        key=lambda item: (
            -item[1],
            item[0].lower(),
        ),
    )

    rows: list[RoomWindowSummary] = []

    if len(ordered) <= MAX_VISIBLE_ROOM_GROUPS:
        rows = [
            RoomWindowSummary(
                label=label,
                quantity=quantity,
            )
            for label, quantity in ordered
        ]

    else:
        visible = ordered[: MAX_VISIBLE_ROOM_GROUPS - 1]

        remaining = ordered[MAX_VISIBLE_ROOM_GROUPS - 1 :]

        rows.extend(
            RoomWindowSummary(
                label=label,
                quantity=quantity,
            )
            for label, quantity in visible
        )

        rows.append(
            RoomWindowSummary(
                label="Otras estancias",
                quantity=sum(quantity for _, quantity in remaining),
            )
        )

    return RoomsTableContent(
        rows=rows,
        total_quantity=sum(counts.values()),
    )
