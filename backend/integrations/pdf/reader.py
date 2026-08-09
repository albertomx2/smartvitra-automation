from pathlib import Path

from pypdf import PdfReader


class PdfTextReader:
    def read(self, path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(path)

        reader = PdfReader(path)

        pages: list[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        return "\n".join(pages)
