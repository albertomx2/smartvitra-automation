from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.prefweb.client import (
    PrefWebClient,
)

QUERY = "PRUEBA CON ALBERTO"


def main() -> None:
    load_dotenv(
        dotenv_path=Path(".env"),
    )

    client = PrefWebClient()

    login = client.login()

    print()
    print("=" * 80)
    print("PREFWEB LOGIN")
    print("=" * 80)
    print("Login: OK")
    print(
        "Resultado login:",
        login.model_dump(),
    )

    documents = client.search_sales_documents(
        query=QUERY,
    )

    print()
    print("=" * 80)
    print("SALES DOCUMENTS")
    print("=" * 80)
    print()

    for document in documents:
        print(
            document.model_dump_json(
                indent=2,
            )
        )
        print()


if __name__ == "__main__":
    main()
