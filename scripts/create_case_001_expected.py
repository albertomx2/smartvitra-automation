from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from backend.domain.proposal import (
    AdvancePayment,
    Commercial,
    CommercialDiscount,
    Customer,
    GlassConfiguration,
    Opening,
    PaymentTerms,
    PriceLine,
    Pricing,
    Proposal,
    ServiceLine,
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
    proposal_date=date(
        2026,
        5,
        6,
    ),
    proposal_number="S00122",
    customer=Customer(
        name="Bonifacio Alonso Madero",
        address="C/ Periana 19, 1º B",
        city="Madrid",
        country="España",
    ),
    commercial=Commercial(
        name="Samanta",
    ),
    odoo_quote_id="S00122",
    openings=[
        Opening(
            id="V1",
            position=1,
            room="Habitación Exterior",
            window_type="Ventana 2 hojas",
            glass=GlassConfiguration(
                description=("Vidrio con Control Solar + argón"),
                control_solar=True,
                low_emissivity=False,
                argon=True,
            ),
        ),
        Opening(
            id="V2",
            position=2,
            room="Habitación interior",
            window_type="Ventana 2 hojas",
            glass=GlassConfiguration(
                description=("Vidrio con bajo Emisivo + argón"),
                control_solar=False,
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
                description=("Vidrio con Bajo Emisivo + argón"),
                control_solar=False,
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
        lines=[
            PriceLine(
                opening_id="V1",
                description="Ventana 2 hojas",
                quantity=Decimal("1.00"),
                list_price=Decimal("1310.00"),
                unit_price=Decimal("1126.60"),
                discount_percentage=Decimal("14.00"),
                subtotal=Decimal("1126.60"),
                tax_percentage=Decimal(21),
            ),
            PriceLine(
                opening_id="V2",
                description="Ventana 2 hojas",
                quantity=Decimal("1.00"),
                list_price=Decimal("1295.00"),
                unit_price=Decimal("1113.70"),
                discount_percentage=Decimal("14.00"),
                subtotal=Decimal("1113.70"),
                tax_percentage=Decimal(21),
            ),
            PriceLine(
                opening_id="V3",
                description="Ventana 1 hoja",
                quantity=Decimal("1.00"),
                list_price=Decimal("1330.00"),
                unit_price=Decimal("1143.80"),
                discount_percentage=Decimal("14.00"),
                subtotal=Decimal("1143.80"),
                tax_percentage=Decimal(21),
            ),
        ],
        services=[
            ServiceLine(
                name="INSTALACIÓN INCLUIDA",
                description=(
                    "Incluye: Forrado y protección de suelos y muebles "
                    "cercanos. Retirada de materiales existentes Limpieza "
                    "y preparación de hueco antes de instalación "
                    "Aislamiento perimetral de hueco Instalación de la "
                    "nueva carpintería. Instalación de todos los remates "
                    "exteriores perimetrales. Sellados estructurales."
                ),
                quantity=Decimal("3.00"),
                list_price=Decimal("130.00"),
                unit_price=Decimal("0.00"),
                discount_percentage=Decimal("100.00"),
                subtotal=Decimal("0.00"),
                tax_percentage=Decimal(21),
            ),
            ServiceLine(
                name="EXTRA ALBAÑILERÍA",
                description=(
                    "Incluye: Aislamiento de capialzado mediante lona de "
                    "roca. Tabicado y enlucido de yeso o pladur NO INCLUYE "
                    "remate de pintura ni su preparación"
                ),
                quantity=Decimal("3.00"),
                list_price=Decimal("60.00"),
                unit_price=Decimal("0.00"),
                discount_percentage=Decimal("100.00"),
                subtotal=Decimal("0.00"),
                tax_percentage=Decimal(21),
            ),
        ],
        discounts=[
            CommercialDiscount(
                name="EXTRA COMERCIAL DEL 3.00%",
                amount=Decimal("-101.52"),
            ),
        ],
        advance_payments=[
            AdvancePayment(
                reference="S00122",
                payment_date=date(2026, 5, 6),
                amount=Decimal("1641.29"),
            ),
            AdvancePayment(
                reference="S00122",
                payment_date=date(2026, 6, 12),
                amount=Decimal("984.77"),
            ),
        ],
        payment_terms=PaymentTerms(
            description=(
                "50 % en concepto de anticipo a la aprobación "
                "del presupuesto. "
                "30 % siete días antes de la fecha de "
                "instalación. "
                "20 % restante a la finalización de la "
                "instalación."
            ),
            deposit_percentage=Decimal(50),
            pre_installation_percentage=Decimal(30),
            final_percentage=Decimal(20),
        ),
    ),
)


output_path = Path("tests/fixtures/case_001/expected.json")

output_path.write_text(
    proposal.model_dump_json(
        indent=2,
    ),
    encoding="utf-8",
)

print(f"Written {output_path}")
