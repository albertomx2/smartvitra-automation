import pytest

from backend.needs.models import (
    CustomerNeedCode,
    CustomerNeedSelection,
)
from backend.needs.service import (
    CustomerNeedsService,
)


def test_customer_needs_are_sorted_by_priority():
    selections = [
        CustomerNeedSelection(
            code=CustomerNeedCode.THERMAL_LOSS,
            priority=3,
        ),
        CustomerNeedSelection(
            code=CustomerNeedCode.ACOUSTIC_NOISE,
            priority=5,
        ),
    ]

    service = CustomerNeedsService()

    result = service.validate(selections)

    assert result[0].code == (CustomerNeedCode.ACOUSTIC_NOISE)

    assert result[1].code == (CustomerNeedCode.THERMAL_LOSS)


def test_customer_need_priority_is_validated():
    with pytest.raises(ValueError):
        CustomerNeedSelection(
            code=CustomerNeedCode.ACOUSTIC_NOISE,
            priority=6,
        )


def test_duplicate_customer_needs_are_rejected():
    selections = [
        CustomerNeedSelection(
            code=CustomerNeedCode.ACOUSTIC_NOISE,
            priority=5,
        ),
        CustomerNeedSelection(
            code=CustomerNeedCode.ACOUSTIC_NOISE,
            priority=3,
        ),
    ]

    service = CustomerNeedsService()

    with pytest.raises(
        ValueError,
        match="Duplicate customer need",
    ):
        service.validate(selections)


def test_need_definition_contains_benefit_categories():
    selection = CustomerNeedSelection(
        code=CustomerNeedCode.ACOUSTIC_NOISE,
        priority=5,
    )

    service = CustomerNeedsService()

    definition = service.get_definition(selection)

    assert "acoustic" in (definition.benefit_categories)
