from __future__ import annotations

import os
from html import escape
from typing import Any
from urllib.parse import urljoin, urlsplit

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
        street: str | None = None,
        street2: str | None = None,
        postal_code: str | None = None,
        city: str | None = None,
    ) -> dict[str, Any]:
        values: dict[str, Any] = {
            "name": name.strip(),
            "email": email.strip(),
            "company_type": "person",
        }

        if phone:
            values["phone"] = phone.strip()
        for field, value in (
            ("street", street),
            ("street2", street2),
            ("zip", postal_code),
            ("city", city),
        ):
            if value:
                values[field] = value.strip()

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
        street: str | None = None,
        street2: str | None = None,
        postal_code: str | None = None,
        city: str | None = None,
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
            street=street,
            street2=street2,
            postal_code=postal_code,
            city=city,
        )

        return created, True

    def get_sale_tax_ids(self, *, rate: float) -> tuple[int, int]:
        """Return the sales tax for goods and services at a PrefWeb rate."""
        if rate == 0:
            return 0, 0

        result = self._request(
            model="account.tax",
            method="search_read",
            payload={
                "domain": [
                    ["type_tax_use", "=", "sale"],
                    ["amount_type", "=", "percent"],
                    ["amount", "=", rate],
                    ["active", "=", True],
                ],
                "fields": ["id", "name"],
                "limit": 30,
            },
        )
        if not isinstance(result, list) or not result:
            raise RuntimeError(f"No active Odoo sales tax found for {rate}%")

        goods = next(
            (row for row in result if str(row["name"]).upper().endswith(" G")),
            result[0],
        )
        services = next(
            (row for row in result if str(row["name"]).upper().endswith(" S")),
            goods,
        )
        return int(goods["id"]), int(services["id"])

    def ensure_prefweb_line_product(self) -> tuple[int, int]:
        """Reuse one technical product; item titles live on quotation lines."""
        code = "SV-PREFWEB-LINE"
        products = self._request(
            model="product.product",
            method="search_read",
            payload={
                "domain": [["default_code", "=", code]],
                "fields": ["id", "uom_id"],
                "limit": 2,
            },
        )
        if not isinstance(products, list) or len(products) > 1:
            raise RuntimeError("Unexpected SmartVitra Odoo product response")
        if not products:
            created = self._request(
                model="product.product",
                method="create",
                payload={
                    "vals_list": {
                        "name": "Partida PrefWeb SmartVitra",
                        "default_code": code,
                        "type": "service",
                        "sale_ok": True,
                    }
                },
            )
            product_id = int(created[0] if isinstance(created, list) else created)
            products = self._request(
                model="product.product",
                method="read",
                payload={"ids": [product_id], "fields": ["id", "uom_id"]},
            )
            if not isinstance(products, list) or len(products) != 1:
                raise RuntimeError("Created Odoo product could not be read back")

        product = products[0]
        uom = product.get("uom_id")
        if not isinstance(uom, list) or not uom:
            raise RuntimeError("Odoo SmartVitra product has no unit of measure")
        return int(product["id"]), int(uom[0])

    def find_sale_quote_by_origin(self, *, origin: str) -> dict[str, Any] | None:
        result = self._request(
            model="sale.order",
            method="search_read",
            payload={
                "domain": [["origin", "=", origin]],
                "fields": [
                    "id",
                    "name",
                    "state",
                    "partner_id",
                    "amount_total",
                    "amount_untaxed",
                ],
                "limit": 2,
            },
        )
        if not isinstance(result, list):
            raise TypeError("Unexpected Odoo sale order response")
        if len(result) > 1:
            raise RuntimeError(f"Multiple Odoo quotes found for {origin}")
        return result[0] if result else None

    def find_sale_quotes_by_prefweb_number(
        self, *, prefweb_number: str
    ) -> list[dict[str, Any]]:
        """Find all sale documents for the stable PrefWeb number, not a job UUID."""
        result = self._request(
            model="sale.order",
            method="search_read",
            payload={
                "domain": [
                    "|",
                    ["x_studio_no_presupuesto_preweb", "=", prefweb_number],
                    ["client_order_ref", "=", prefweb_number],
                ],
                "fields": [
                    "id",
                    "name",
                    "state",
                    "origin",
                    "partner_id",
                    "amount_total",
                ],
                "order": "id desc",
                "limit": 100,
            },
        )
        if not isinstance(result, list):
            raise TypeError("Unexpected Odoo sale order response")
        return result

    def update_sale_quote(
        self,
        *,
        quote_id: int,
        partner_id: int,
        origin: str,
        reference: str,
        prefweb_number: str,
        payment_term: str | None,
        lines: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Replace lines on a SmartVitra draft; never modify sent/confirmed sales."""
        quotes = self.find_sale_quotes_by_prefweb_number(prefweb_number=prefweb_number)
        existing = next(
            (quote for quote in quotes if int(quote["id"]) == quote_id), None
        )
        if existing is None:
            raise RuntimeError("Odoo quotation changed; review it before regenerating")
        if existing["state"] != "draft":
            raise RuntimeError("Only a draft Odoo quotation can be overwritten")
        if not str(existing.get("origin") or "").startswith("SmartVitra generation "):
            raise RuntimeError(
                "A manually managed Odoo quotation cannot be overwritten"
            )
        if int(existing["partner_id"][0]) != partner_id:
            raise RuntimeError("Odoo quotation belongs to another customer")

        result = self._request(
            model="sale.order",
            method="write",
            payload={
                "ids": [quote_id],
                "vals": {
                    "origin": origin,
                    "client_order_ref": reference,
                    "x_studio_no_presupuesto_preweb": prefweb_number,
                    "note": (
                        f"<p>Condiciones de pago de PrefWeb: {escape(payment_term)}</p>"
                        if payment_term
                        else ""
                    ),
                    "order_line": [[5, 0, 0], *[[0, 0, line] for line in lines]],
                },
            },
            timeout=120,
        )
        if result is not True:
            raise RuntimeError("Odoo did not confirm quotation update")
        quote = self.find_sale_quote_by_origin(origin=origin)
        if quote is None or int(quote["id"]) != quote_id:
            raise RuntimeError("Updated Odoo quotation could not be read back")
        return quote

    def create_sale_quote(
        self,
        *,
        partner_id: int,
        origin: str,
        reference: str,
        prefweb_number: str,
        payment_term: str | None,
        lines: list[dict[str, Any]],
    ) -> dict[str, Any]:
        existing = self.find_sale_quote_by_origin(origin=origin)
        if existing is not None:
            if existing["state"] != "draft":
                raise RuntimeError("Existing Odoo quote is no longer a draft")
            if int(existing["partner_id"][0]) != partner_id:
                raise RuntimeError("Existing Odoo quote belongs to another customer")
            return existing

        values: dict[str, Any] = {
            "partner_id": partner_id,
            "origin": origin,
            "client_order_ref": reference,
            "x_studio_no_presupuesto_preweb": prefweb_number,
            "order_line": [[0, 0, line] for line in lines],
        }
        if payment_term:
            values["note"] = (
                f"<p>Condiciones de pago de PrefWeb: {escape(payment_term)}</p>"
            )

        result = self._request(
            model="sale.order",
            method="create",
            payload={"vals_list": values},
            timeout=120,
        )
        if isinstance(result, list):
            if len(result) != 1:
                raise RuntimeError("Unexpected Odoo quote creation response")
            quote_id = int(result[0])
        else:
            quote_id = int(result)

        quote = self.find_sale_quote_by_origin(origin=origin)
        if quote is None or int(quote["id"]) != quote_id:
            raise RuntimeError("Created Odoo quote could not be read back")
        return quote

    def fetch_sale_quote_pdf(self, *, quote_id: int) -> bytes:
        """Download Odoo's own quotation report using its scoped portal token."""
        portal_path = self._request(
            model="sale.order",
            method="get_portal_url",
            payload={"ids": [quote_id]},
        )
        if not isinstance(portal_path, str) or not portal_path:
            raise RuntimeError("Odoo did not return a quotation portal URL")

        url = urljoin(f"{self._base_url}/", portal_path)
        base = urlsplit(self._base_url)
        target = urlsplit(url)
        if (target.scheme, target.netloc) != (base.scheme, base.netloc):
            raise RuntimeError("Odoo quotation portal URL has an unexpected host")

        response = requests.get(
            url,
            params={"report_type": "pdf", "download": "true"},
            headers={"Odoo-Link-Preview": "True"},
            timeout=90,
            allow_redirects=False,
        )
        if (
            response.status_code != 200
            or "application/pdf" not in response.headers.get("Content-Type", "")
            or not response.content.startswith(b"%PDF-")
        ):
            raise RuntimeError(
                f"Odoo quotation PDF unavailable (HTTP {response.status_code})"
            )
        return response.content

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
        has_odoo_quote: bool = False,
    ) -> int:
        first_name = (
            partner_name.strip().split()[0] if partner_name.strip() else "cliente"
        )

        additional_line = ""

        if has_manual_attachments:
            additional_line = (
                "<li>Documentación adicional " "incluida en la propuesta.</li>"
            )

        if has_odoo_quote:
            additional_line += "<li>El presupuesto detallado.</li>"

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
