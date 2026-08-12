from pathlib import Path

import pytest

from backend.integrations.prefweb.parser import (
    PrefWebSalesDocumentParser,
)

HTML_PATH = Path("tmp/prefweb/1000095530_1.html")


@pytest.mark.skipif(
    not HTML_PATH.exists(),
    reason=("Run experiments.prefweb." "inspect_sales_document first"),
)
def test_prefweb_parser_real_snapshot():
    html = HTML_PATH.read_text(
        encoding="utf-8",
    )

    document = PrefWebSalesDocumentParser().parse(
        html,
    )

    assert document.number == 1000095530

    assert document.version == 1

    assert document.customer.name == ("PRUEBA CON ALBERTO")

    assert len(document.items) >= 2

    assert document.items[0].reference == ("2203V")

    assert document.items[1].reference == ("3302V")
