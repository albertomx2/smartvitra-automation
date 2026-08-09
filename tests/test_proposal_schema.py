from decimal import Decimal

from backend.domain.enums import ProposalStatus
from backend.domain.proposal import (
    Customer,
    GlassConfiguration,
    Opening,
    Pricing,
    Proposal,
)


def test_create_basic_proposal():
    proposal = Proposal(
        proposal_number="S00122",
        customer=Customer(
            name="Test Customer",
            city="Madrid",
            country="España",
        ),
        openings=[
            Opening(
                id="V1",
                position=1,
                room="Habitación Exterior",
                window_type="Ventana 2 hojas",
                glass=GlassConfiguration(
                    description="Vidrio con Control Solar + argón",
                    control_solar=True,
                    argon=True,
                ),
            )
        ],
        pricing=Pricing(
            currency="EUR",
            subtotal=Decimal("3282.58"),
            tax_total=Decimal("689.35"),
            total=Decimal("3971.93"),
        ),
    )

    assert proposal.proposal_number == "S00122"
    assert proposal.status == ProposalStatus.DRAFT

    assert len(proposal.openings) == 1

    assert proposal.openings[0].id == "V1"

    assert proposal.openings[0].glass is not None
    assert proposal.openings[0].glass.argon is True

    assert proposal.pricing is not None
    assert proposal.pricing.total == Decimal("3971.93")
