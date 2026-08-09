from backend.needs.catalog import (
    NEED_DEFINITIONS,
)
from backend.needs.models import (
    CustomerNeedDefinition,
    CustomerNeedSelection,
)


class CustomerNeedsService:
    def validate(
        self,
        selections: list[CustomerNeedSelection],
    ) -> list[CustomerNeedSelection]:
        seen = set()

        for selection in selections:
            if selection.code in seen:
                raise ValueError("Duplicate customer need: " f"{selection.code}")

            if selection.code not in NEED_DEFINITIONS:
                raise ValueError("Unknown customer need: " f"{selection.code}")

            seen.add(selection.code)

        return sorted(
            selections,
            key=lambda item: item.priority,
            reverse=True,
        )

    def get_definition(
        self,
        selection: CustomerNeedSelection,
    ) -> CustomerNeedDefinition:
        return NEED_DEFINITIONS[selection.code]
