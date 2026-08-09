import re
from decimal import Decimal


def parse_euro_decimal(value: str) -> Decimal:
    cleaned = value.strip()

    cleaned = cleaned.replace("\u200b", "")
    cleaned = cleaned.replace("€", "")
    cleaned = cleaned.replace(".", "")
    cleaned = cleaned.replace(",", ".")

    cleaned = cleaned.replace("−", "-")
    cleaned = cleaned.replace("–", "-")
    cleaned = cleaned.replace("\u200b", "")

    return Decimal(cleaned)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    return text
