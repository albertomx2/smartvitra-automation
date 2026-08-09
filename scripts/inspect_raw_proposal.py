from pathlib import Path

from backend.integrations.pdf.parser import (
    PdfProposalParser,
)
from backend.integrations.pdf.reader import (
    PdfTextReader,
)

pdf_path = Path("assets/examples/Pedido - S00122.pdf")

reader = PdfTextReader()
parser = PdfProposalParser()

text = reader.read(pdf_path)

raw = parser.parse(text)

print(
    raw.model_dump_json(
        indent=2,
    )
)
