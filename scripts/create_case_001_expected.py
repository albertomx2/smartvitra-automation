from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from backend.domain.proposal import (
    Customer,
    GlassConfiguration,
    Opening,
    PaymentTerms,
    Pricing,
    Proposal,
)

proposal = Proposal(
    id=UUID("00000000-0000-0000-0000-000000000001"),
    created_at=datetime(
        2026,
        5,
        6,
        12,
        0,
        tzinfo=timezone.utc,
    ),
    updated_at=datetime(
        2026,
        5,
        6,
        12,
        0,
        tzinfo=timezone.utc,
    ),
    proposal_date=datetime(2026, 5, 6).date(),
    proposal_number="S00122",
    customer=Customer(
        name="TEST CUSTOMER",
        city="Madrid",
        country="España",
    ),
    odoo_quote_id="S00122",
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
        ),
        Opening(
            id="V2",
            position=2,
            room="Habitación interior",
            window_type="Ventana 2 hojas",
            glass=GlassConfiguration(
                description="Vidrio con bajo Emisivo + argón",
                low_emissivity=True,
                argon=True,
            ),
        ),
        Opening(
            id="V3",
            position=3,
            room="Habitación puerta",
            window_type="Ventana 1 hoja",
            glass=GlassConfiguration(
                description="Vidrio con Bajo Emisivo + argón",
                low_emissivity=True,
                argon=True,
            ),
        ),
    ],
    pricing=Pricing(
        currency="EUR",
        usual_cost=Decimal("4403.48"),
        discount_total=Decimal("1120.90"),
        subtotal=Decimal("3282.58"),
        tax_total=Decimal("689.35"),
        total=Decimal("3971.93"),
        payment_terms=PaymentTerms(
            description=(
                "50 % anticipo, "
                "30 % siete días antes de instalación, "
                "20 % a la finalización."
            ),
            deposit_percentage=Decimal(50),
            pre_installation_percentage=Decimal(30),
            final_percentage=Decimal(20),
        ),
    ),
)


output_path = Path("tests/fixtures/case_001/expected.json")

output_path.write_text(
    proposal.model_dump_json(indent=2),
    encoding="utf-8",
)

print(f"Written {output_path}")
