from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.prefweb.client import (
    PrefWebClient,
)
from backend.integrations.prefweb.parser import (
    PrefWebSalesDocumentParser,
)

NUMBER = 1000095530
VERSION = 1

OUTPUT_DIR = Path("tmp/prefweb")


def main() -> None:
    load_dotenv(
        dotenv_path=Path(".env"),
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    client = PrefWebClient()

    login = client.login()

    print()
    print("=" * 80)
    print("PREFWEB LOGIN")
    print("=" * 80)

    print(
        "Login:",
        "OK" if login.valid_login else "FAILED",
    )

    for entity in login.available_entities:
        print(
            "Entidad:",
            entity.name,
        )

    print()
    print("=" * 80)
    print("DOWNLOADING SALES DOCUMENT")
    print("=" * 80)

    html = client.get_sales_document_html(
        number=NUMBER,
        version=VERSION,
    )

    html_path = OUTPUT_DIR / f"{NUMBER}_{VERSION}.html"

    html_path.write_text(
        html,
        encoding="utf-8",
    )

    print(
        "HTML:",
        html_path,
    )

    parser = PrefWebSalesDocumentParser()

    document = parser.parse(
        html,
    )

    json_path = OUTPUT_DIR / f"{NUMBER}_{VERSION}.json"

    json_path.write_text(
        document.model_dump_json(
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 80)
    print("PARSED SALES DOCUMENT")
    print("=" * 80)
    print()

    print(
        document.model_dump_json(
            indent=2,
        )
    )

    print()
    print(
        "JSON:",
        json_path,
    )


if __name__ == "__main__":
    main()
