from decimal import Decimal
from pathlib import Path

from backend.integrations.pdf.parser import (
    PdfProposalParser,
)
from backend.integrations.pdf.reader import (
    PdfTextReader,
)
from backend.services.proposal_normalizer import (
    ProposalNormalizer,
)


def test_normalize_s00122():
    pdf_path = Path("assets/examples/Pedido - S00122.pdf")

    reader = PdfTextReader()
    parser = PdfProposalParser()
    normalizer = ProposalNormalizer()

    text = reader.read(pdf_path)
    raw = parser.parse(text)
    proposal = normalizer.normalize(raw)

    assert proposal.proposal_number == "S00122"

    assert proposal.customer.name == ("Bonifacio Alonso Madero")

    assert proposal.commercial is not None
    assert proposal.commercial.name == "Samanta"

    assert len(proposal.openings) == 3

    v1 = proposal.openings[0]
    v2 = proposal.openings[1]
    v3 = proposal.openings[2]

    assert v1.id == "V1"
    assert v1.glass is not None
    assert v1.glass.control_solar is True
    assert v1.glass.argon is True

    assert v2.glass is not None
    assert v2.glass.low_emissivity is True
    assert v2.glass.argon is True

    assert v3.glass is not None
    assert v3.glass.low_emissivity is True

    assert proposal.pricing is not None

    assert proposal.pricing.subtotal == Decimal("3282.58")

    assert proposal.pricing.tax_total == Decimal("689.35")

    assert proposal.pricing.total == Decimal("3971.93")
