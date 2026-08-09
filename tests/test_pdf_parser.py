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

    assert raw.payment_terms is not None

    assert "50 % en concepto de anticipo" in raw.payment_terms.text
