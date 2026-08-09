from pathlib import Path

from backend.integrations.pdf.reader import PdfTextReader

pdf_path = Path("assets/examples/Pedido - S00122.pdf")

reader = PdfTextReader()

text = reader.read(pdf_path)

print(text)
