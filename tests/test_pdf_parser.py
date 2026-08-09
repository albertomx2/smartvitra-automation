from decimal import Decimal
from pathlib import Path

from backend.integrations.pdf.parser import PdfProposalParser
from backend.integrations.pdf.reader import PdfTextReader


def test_parse_s00122():
    pdf_path = Path("assets/examples/Pedido - S00122.pdf")

    reader = PdfTextReader()
    parser = PdfProposalParser()

    text = reader.read(pdf_path)

    raw = parser.parse(text)

    assert raw.proposal_number == "S00122"

    assert str(raw.proposal_date) == "2026-05-06"

    assert raw.commercial_name == "Samanta"

    assert raw.customer_name == ("Bonifacio Alonso Madero")

    assert raw.customer_address == ("C/ Periana 19, 1º B")

    assert raw.customer_city == "Madrid"
    assert raw.customer_country == "España"

    assert raw.usual_cost == Decimal("4403.48")
    assert raw.discount_total == Decimal("1120.90")

    assert raw.subtotal == Decimal("3282.58")
    assert raw.tax_total == Decimal("689.35")
    assert raw.total == Decimal("3971.93")

    assert len(raw.openings) == 3

    assert raw.openings[0].identifier == "V1"
    assert raw.openings[0].position == 1
    assert raw.openings[0].room == ("Habitación Exterior")

    assert raw.openings[1].identifier == "V2"

    assert raw.openings[2].identifier == "V3"

    assert raw.openings[0].quantity == Decimal("1.00")

    assert raw.openings[0].list_price == Decimal("1310.00")

    assert raw.openings[0].discounted_unit_price == Decimal("1126.60")

    assert raw.openings[0].discount_percentage == Decimal("14.00")

    assert raw.openings[0].tax_percentage == Decimal(21)

    assert raw.openings[0].subtotal == Decimal("1126.60")

    assert raw.openings[1].subtotal == Decimal("1113.70")

    assert raw.openings[2].subtotal == Decimal("1143.80")

    assert len(raw.services) == 2

    installation = raw.services[0]

    assert installation.name == ("INSTALACIÓN INCLUIDA")
    assert installation.quantity == Decimal("3.00")
    assert installation.list_price == Decimal("130.00")
    assert installation.discounted_unit_price == Decimal("0.00")
    assert installation.discount_percentage == Decimal("100.00")
    assert installation.tax_percentage == Decimal(21)
    assert installation.subtotal == Decimal("0.00")

    masonry = raw.services[1]

    assert masonry.name == "EXTRA ALBAÑILERÍA"
    assert masonry.quantity == Decimal("3.00")
    assert masonry.list_price == Decimal("60.00")
    assert masonry.subtotal == Decimal("0.00")

    assert len(raw.discounts) == 1

    commercial_discount = raw.discounts[0]

    assert commercial_discount.name == ("EXTRA COMERCIAL DEL 3.00%")

    assert commercial_discount.amount == Decimal("-101.52")

    assert len(raw.advance_payments) == 2

    first_advance = raw.advance_payments[0]
    second_advance = raw.advance_payments[1]

    assert first_advance.reference == "S00122"
    assert str(first_advance.payment_date) == ("2026-05-06")
    assert first_advance.amount == Decimal("1641.29")

    assert second_advance.reference == "S00122"
    assert str(second_advance.payment_date) == ("2026-06-12")
    assert second_advance.amount == Decimal("984.77")

    assert raw.payment_terms is not None

    assert "50 % en concepto de anticipo" in raw.payment_terms.text
