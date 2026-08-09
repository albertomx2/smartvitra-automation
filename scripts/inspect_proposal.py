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

pdf_path = Path("assets/examples/Pedido - S00122.pdf")

reader = PdfTextReader()
parser = PdfProposalParser()
normalizer = ProposalNormalizer()

text = reader.read(pdf_path)

raw = parser.parse(text)

proposal = normalizer.normalize(raw)

print(
    proposal.model_dump_json(
        indent=2,
    )
)
