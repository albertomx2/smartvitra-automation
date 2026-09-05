from __future__ import annotations

import os
from typing import Any

import requests


class OdooClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._base_url = (base_url or os.getenv("ODOO_URL") or "").rstrip("/")

        self._api_key = api_key or os.getenv("ODOO_API_KEY") or ""

        if not self._base_url:
            raise ValueError("ODOO_URL is required")

        if not self._api_key:
            raise ValueError("ODOO_API_KEY is required")

    def _request(
        self,
        *,
        model: str,
        method: str,
        payload: dict[str, Any],
        timeout: int = 30,
    ) -> Any:
        response = requests.post(
            (f"{self._base_url}/json/2/" f"{model}/{method}"),
            headers={
                "Authorization": (f"bearer {self._api_key}"),
                "Content-Type": "application/json",
                "User-Agent": ("SmartVitra Automation"),
            },
            json=payload,
            timeout=timeout,
        )

        if not response.ok:
            raise RuntimeError(
                "Odoo request failed: "
                f"{model}.{method} "
                f"HTTP {response.status_code}: "
                f"{response.text[:1000]}"
            )

        if not response.content:
            return None

        return response.json()

    def search_partner_by_email(
        self,
        *,
        email: str,
    ) -> dict[str, Any] | None:
        value = email.strip()
        normalized = value.lower()

        if not value:
            raise ValueError("Customer email is required")

        result = self._request(
            model="res.partner",
            method="search_read",
            payload={
                "domain": [
                    "|",
                    [
                        "email_normalized",
                        "=",
                        normalized,
                    ],
                    [
                        "email",
                        "=ilike",
                        value,
                    ],
                ],
                "fields": [
                    "id",
                    "name",
                    "email",
                    "phone",
                    "vat",
                    "company_type",
                    "active",
                ],
                "limit": 2,
            },
        )

        if not isinstance(result, list):
            raise TypeError("Unexpected Odoo partner response")

        if not result:
            return None

        if len(result) > 1:
            raise RuntimeError("Multiple Odoo partners found " f"for email {email!r}")

        return result[0]

    def create_partner(
        self,
        *,
        name: str,
        email: str,
        phone: str | None = None,
    ) -> dict[str, Any]:
        values: dict[str, Any] = {
            "name": name.strip(),
            "email": email.strip(),
            "company_type": "person",
        }

        if phone:
            values["phone"] = phone.strip()

        result = self._request(
            model="res.partner",
            method="create",
            payload={
                "vals_list": values,
            },
        )

        if isinstance(result, list):
            if len(result) != 1:
                raise RuntimeError("Unexpected Odoo create response")

            partner_id = int(result[0])
        else:
            partner_id = int(result)

        partners = self._request(
            model="res.partner",
            method="read",
            payload={
                "ids": [partner_id],
                "fields": [
                    "id",
                    "name",
                    "email",
                    "phone",
                    "company_type",
                ],
            },
        )

        if not isinstance(partners, list) or len(partners) != 1:
            raise RuntimeError("Created Odoo partner could not " "be read back")

        return partners[0]

    def find_or_create_partner(
        self,
        *,
        name: str,
        email: str,
        phone: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        existing = self.search_partner_by_email(
            email=email,
        )

        if existing is not None:
            return existing, False

        created = self.create_partner(
            name=name,
            email=email,
            phone=phone,
        )

        return created, True

    def create_attachment(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> int:
        import base64

        encoded = base64.b64encode(
            content,
        ).decode("ascii")

        result = self._request(
            model="ir.attachment",
            method="create",
            payload={
                "vals_list": {
                    "name": filename,
                    "datas": encoded,
                    "mimetype": content_type,
                    "type": "binary",
                },
            },
            timeout=120,
        )

        if isinstance(result, list):
            if len(result) != 1:
                raise RuntimeError("Unexpected attachment create response")

            return int(result[0])

        return int(result)

    def send_proposal_email(
        self,
        *,
        partner_id: int,
        partner_name: str,
        attachment_ids: list[int],
        has_manual_attachments: bool,
    ) -> int:
        first_name = (
            partner_name.strip().split()[0] if partner_name.strip() else "cliente"
        )

        additional_line = ""

        if has_manual_attachments:
            additional_line = (
                "<li>Documentación adicional " "incluida en la propuesta.</li>"
            )

        body_html = f"""
<p>Hola {first_name},</p>

<p>
Desde SmartVitra le enviamos la propuesta que hemos
preparado para su vivienda.
</p>

<p>En los archivos adjuntos podrá encontrar:</p>

<ul>
<li>Una presentación con los detalles de la propuesta
y la instalación.</li>
<li>Un vídeo explicativo donde desarrollamos el trabajo
planteado.</li>
{additional_line}
</ul>

<p>
Si tiene cualquier duda sobre la propuesta,
estaremos encantados de ayudarle.
</p>

<p>
Un saludo,<br>
<strong>SmartVitra</strong>
</p>
""".strip()

        result = self._request(
            model="mail.mail",
            method="create",
            payload={
                "vals_list": {
                    "subject": "Su propuesta SmartVitra",
                    "body_html": body_html,
                    "recipient_ids": [
                        [
                            6,
                            0,
                            [partner_id],
                        ]
                    ],
                    "attachment_ids": [
                        [
                            6,
                            0,
                            attachment_ids,
                        ]
                    ],
                    "model": "res.partner",
                    "res_id": partner_id,
                },
            },
        )

        if isinstance(result, list):
            if len(result) != 1:
                raise RuntimeError("Unexpected mail create response")

            mail_id = int(result[0])
        else:
            mail_id = int(result)

        self._request(
            model="mail.mail",
            method="send",
            payload={
                "ids": [mail_id],
            },
            timeout=120,
        )

        return mail_id
