import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_URL = "https://www.prefweb.com/Sumum/PrefWeb"

NUMBER = 1000095530
VERSION = 1

OUTPUT_DIR = Path("tmp/prefweb")


def print_cookies(
    session: requests.Session,
    *,
    title: str,
) -> None:
    print()
    print(title)

    if not session.cookies:
        print("  <sin cookies>")
        return

    for cookie in session.cookies:
        print(f"  {cookie.name}=" f"{cookie.value[:25]}...")


def main() -> None:
    load_dotenv(
        dotenv_path=Path(".env"),
    )

    email = os.getenv("PREFWEB_EMAIL")

    password = os.getenv("PREFWEB_PASSWORD")

    if not email or not password:
        raise RuntimeError("Faltan PREFWEB_EMAIL " "o PREFWEB_PASSWORD")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    session = requests.Session()

    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
            "Accept-Language": ("es-ES,es;q=0.9"),
        }
    )

    print()
    print("=" * 80)
    print("1. INITIAL PREFWEB PAGE")
    print("=" * 80)

    root_response = session.get(
        f"{BASE_URL}/",
        timeout=30,
    )

    print(
        "Status:",
        root_response.status_code,
    )
    print(
        "URL final:",
        root_response.url,
    )

    print_cookies(
        session,
        title="Cookies tras GET inicial:",
    )

    print()
    print("=" * 80)
    print("2. CHECK LOGIN")
    print("=" * 80)

    login_response = session.post(
        f"{BASE_URL}/Home/CheckLogin",
        json={
            "email": email,
            "password": password,
        },
        headers={
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.prefweb.com",
            "Referer": f"{BASE_URL}/",
        },
        timeout=30,
    )

    print(
        "Status:",
        login_response.status_code,
    )
    print(
        "URL final:",
        login_response.url,
    )
    print(
        "JSON:",
        login_response.json(),
    )

    print_cookies(
        session,
        title="Cookies tras CheckLogin:",
    )

    print()
    print("=" * 80)
    print("3. SALES DOCUMENT EDIT")
    print("=" * 80)

    edit_response = session.get(
        f"{BASE_URL}/SalesDocuments/Edit",
        params={
            "number": NUMBER,
            "version": VERSION,
        },
        timeout=30,
        allow_redirects=True,
    )

    print(
        "Status:",
        edit_response.status_code,
    )
    print(
        "URL solicitada:",
        edit_response.request.url,
    )
    print(
        "URL final:",
        edit_response.url,
    )

    print(
        "Historial redirects:",
        len(edit_response.history),
    )

    for index, response in enumerate(
        edit_response.history,
        start=1,
    ):
        print(f"  {index}. " f"{response.status_code} " f"{response.url}")

        print(
            "     Location:",
            response.headers.get("Location"),
        )

    print_cookies(
        session,
        title="Cookies finales:",
    )

    html_path = OUTPUT_DIR / "debug_edit_response.html"

    html_path.write_text(
        edit_response.text,
        encoding="utf-8",
    )

    print()
    print(
        "Contiene CustomerName:",
        "CustomerName" in edit_response.text,
    )

    print(
        "Contiene CheckLogin:",
        "CheckLogin" in edit_response.text,
    )

    print(
        "Contiene Iniciar sesión:",
        "Iniciar sesión" in edit_response.text,
    )

    print()
    print(
        "HTML guardado en:",
        html_path,
    )

    print()
    print("Primeros 500 caracteres:")
    print("-" * 80)
    print(edit_response.text[:500])


if __name__ == "__main__":
    main()
