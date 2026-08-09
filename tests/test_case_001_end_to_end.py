import json
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


def test_case_001_end_to_end():
    pdf_path = Path("assets/examples/Pedido - S00122.pdf")

    expected_path = Path("tests/fixtures/case_001/expected.json")

    reader = PdfTextReader()
    parser = PdfProposalParser()
    normalizer = ProposalNormalizer()

    text = reader.read(pdf_path)

    raw = parser.parse(text)

    proposal = normalizer.normalize(raw)

    actual = proposal.model_dump(mode="json")

    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    dynamic_fields = (
        "id",
        "created_at",
        "updated_at",
    )

    for field in dynamic_fields:
        actual.pop(field, None)
        expected.pop(field, None)

    assert actual == expected
