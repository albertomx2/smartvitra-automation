from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.prefweb.service import (
    PrefWebService,
)

QUERY = "PRUEBA CON ALBERTO"


def main() -> None:
    load_dotenv(
        dotenv_path=Path(".env"),
    )

    service = PrefWebService()

    print()
    print("=" * 80)
    print("LOGIN")
    print("=" * 80)

    service.login()

    print("OK")

    print()
    print("=" * 80)
    print("SEARCH")
    print("=" * 80)

    projects = service.search_projects(
        query=QUERY,
    )

    for project in projects:
        print(
            f"{project.alias_number} | "
            f"{project.customer_name} | "
            f"v{project.version} | "
            f"{project.final_price:.2f}"
            f"{project.currency_symbol or '€'}"
        )

    if not projects:
        raise RuntimeError("No projects found")

    selected = projects[0]

    print()
    print("=" * 80)
    print("SELECTED PROJECT")
    print("=" * 80)

    print(
        "Number:",
        selected.number,
    )
    print(
        "Version:",
        selected.version,
    )

    versions = service.get_versions(
        number=selected.number,
    )

    print()
    print("=" * 80)
    print("AVAILABLE VERSIONS")
    print("=" * 80)

    for version in versions:
        active_marker = " [ACTIVE]" if version.is_active else ""

        print(f"{version.version}: " f"{version.version_name}" f"{active_marker}")

    project = service.get_project(
        summary=selected,
    )

    print()
    print("=" * 80)
    print("FULL PROJECT")
    print("=" * 80)
    print()

    print(
        project.model_dump_json(
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
