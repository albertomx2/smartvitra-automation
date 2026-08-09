from pathlib import Path

from backend.integrations.pdf.reader import PdfTextReader


def test_read_s00122_pdf():
    pdf_path = Path("assets/examples/Pedido - S00122.pdf")

    reader = PdfTextReader()

    text = reader.read(pdf_path)

    assert "S00122" in text
    assert "3.971,93" in text
    assert "Ventana 2 hojas" in text
