from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag

HTML_PATH = Path("tmp/prefweb/debug_edit_response.html")

KEYWORDS = (
    "CheckLogin",
    "AvailableEntities",
    "ValidLogin",
    "EntityId",
    "EntityName",
    "login",
    "entity",
)


def main() -> None:
    html = HTML_PATH.read_text(
        encoding="utf-8",
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    print()
    print("=" * 80)
    print("INLINE SCRIPTS RELACIONADOS")
    print("=" * 80)

    found_inline = False

    for index, script in enumerate(
        soup.find_all("script"),
        start=1,
    ):
        if not isinstance(
            script,
            Tag,
        ):
            continue

        text = script.get_text(
            "\n",
            strip=False,
        )

        if not text:
            continue

        if any(keyword.lower() in text.lower() for keyword in KEYWORDS):
            found_inline = True

            print()
            print(f"--- SCRIPT INLINE {index} ---")
            print(text[:12000])

    if not found_inline:
        print("No se encontraron scripts inline " "relacionados.")

    print()
    print("=" * 80)
    print("SCRIPTS EXTERNOS")
    print("=" * 80)

    for script in soup.find_all(
        "script",
        src=True,
    ):
        if not isinstance(
            script,
            Tag,
        ):
            continue

        src = script.get(
            "src",
        )

        if isinstance(
            src,
            str,
        ):
            print(src)


if __name__ == "__main__":
    main()
