from backend.config import settings  # noqa: F401
from backend.integrations.prefweb.service import PrefWebService


def main() -> None:
    service = PrefWebService()

    print("=" * 80)
    print("EMPTY SEARCH")
    print("=" * 80)

    projects = service.search_projects(
        query="",
        page=1,
        page_size=20,
    )

    print("Resultados:", len(projects))

    for project in projects:
        print(
            project.alias_number,
            "|",
            project.customer_name,
            "|",
            project.final_price,
        )


if __name__ == "__main__":
    main()
