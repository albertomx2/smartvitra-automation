from pathlib import Path
from urllib.parse import urljoin

from backend.integrations.prefweb.client import PrefWebClient

NUMBER = 1000095530
VERSION = 1
ITEM_ID = "89cf2491-887b-4e3e-abc7-cd081409ab04"


def main() -> None:
    client = PrefWebClient()

    print("=" * 80)
    print("LOGIN")
    print("=" * 80)

    client.login()

    print("OK")

    print()
    print("=" * 80)
    print("GET SALES ITEM IMAGE PATH")
    print("=" * 80)

    endpoint = "https://www.prefweb.com/" "Sumum/PrefWeb/Images/GetSalesItemImageAsync"

    response = client.session.get(
        endpoint,
        params={
            "number": NUMBER,
            "version": VERSION,
            "type": "Design",
            "subtype": "None",
            "itemId": ITEM_ID,
            "width": 200,
            "height": 200,
            "imageType": 5,
        },
        timeout=30,
    )
    response.raise_for_status()

    image_path = response.json()

    print(f"Path: {image_path}")

    print()
    print("=" * 80)
    print("DOWNLOAD SVG")
    print("=" * 80)

    image_url = urljoin(
        "https://www.prefweb.com",
        image_path,
    )

    svg_response = client.session.get(
        image_url,
        timeout=30,
    )
    svg_response.raise_for_status()

    svg = svg_response.text

    print(f"Status: {svg_response.status_code}")
    print(f"Content-Type: {svg_response.headers.get('Content-Type')}")
    print(f"Bytes: {len(svg_response.content)}")
    print(f"Contains <svg: {'<svg' in svg}")

    output = Path(
        "tmp/prefweb/images/1000095530_1_" "89cf2491-887b-4e3e-abc7-cd081409ab04.svg"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        svg,
        encoding="utf-8",
    )

    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
