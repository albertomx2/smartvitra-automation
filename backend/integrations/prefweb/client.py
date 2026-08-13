import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

import backend.config.settings  # noqa: F401
from backend.integrations.prefweb.models import (
    PrefWebDocumentVersion,
    PrefWebEntity,
    PrefWebLoginResult,
    PrefWebSalesDocumentSummary,
)


class PrefWebAuthenticationError(RuntimeError):
    pass


class PrefWebClient:
    BASE_URL = "https://www.prefweb.com/Sumum/PrefWeb"

    def __init__(
        self,
        *,
        email: str | None = None,
        password: str | None = None,
        entity_id: str | None = None,
    ) -> None:
        self._email = email or os.getenv("PREFWEB_EMAIL")

        self._password = password or os.getenv("PREFWEB_PASSWORD")

        self._entity_id = entity_id or os.getenv("PREFWEB_ENTITY_ID")

        if not self._email:
            raise ValueError("PREFWEB_EMAIL is not configured")

        if not self._password:
            raise ValueError("PREFWEB_PASSWORD is not configured")

        self._session = requests.Session()

        self._session.headers.update(
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

        self._authenticated = False

    @property
    def session(
        self,
    ) -> requests.Session:
        return self._session

    def get_sales_item_image_path(
        self,
        *,
        number: int,
        version: int,
        item_id: str,
        item_type: str = "Design",
        item_subtype: str = "None",
        width: int = 200,
        height: int = 200,
        image_type: int = 5,
    ) -> str:
        if not self._authenticated:
            self.login()

        response = self._session.get(
            (f"{self.BASE_URL}/" "Images/GetSalesItemImageAsync"),
            params={
                "number": str(number),
                "version": str(version),
                "type": item_type,
                "subtype": item_subtype,
                "itemId": item_id,
                "width": str(width),
                "height": str(height),
                "imageType": str(image_type),
            },
            timeout=30,
        )

        response.raise_for_status()

        image_path = response.json()

        if not isinstance(image_path, str):
            raise TypeError("PrefWeb returned an invalid " "sales item image path")

        if not image_path.lower().endswith(".svg"):
            raise RuntimeError("PrefWeb sales item image " "is not an SVG")

        return image_path

    def get_sales_item_svg(
        self,
        *,
        number: int,
        version: int,
        item_id: str,
        item_type: str = "Design",
        item_subtype: str = "None",
    ) -> str:
        image_path = self.get_sales_item_image_path(
            number=number,
            version=version,
            item_id=item_id,
            item_type=item_type,
            item_subtype=item_subtype,
        )

        image_url = urljoin(
            "https://www.prefweb.com",
            image_path,
        )

        response = self._session.get(
            image_url,
            timeout=30,
        )

        response.raise_for_status()

        svg = response.text

        if "<svg" not in svg:
            raise RuntimeError("PrefWeb sales item image " "response is not SVG")

        return svg

    def login(
        self,
    ) -> PrefWebLoginResult:
        login_page = self._get_login_page()

        token = self._extract_verification_token(
            login_page.text,
        )

        form_action = self._extract_login_form_action(
            login_page.text,
        )

        check_result = self._check_login()

        entity = self._select_entity(
            check_result.available_entities,
        )

        self._submit_login_form(
            form_action=form_action,
            verification_token=token,
            entity=entity,
        )

        self._authenticated = True

        return check_result

    def ensure_login(
        self,
    ) -> None:
        if not self._authenticated:
            self.login()

    def search_sales_documents(
        self,
        *,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> list[PrefWebSalesDocumentSummary]:
        self.ensure_login()

        query = query.strip()

        if query:
            safe_query = query.replace(
                "'",
                "''",
            )

            filter_expression = (
                "("
                f"AliasNumber~contains~'{safe_query}'"
                "~or~"
                f"CustomerName~contains~'{safe_query}'"
                "~or~"
                f"CustomerNif~contains~'{safe_query}'"
                "~or~"
                f"ShippingWork~contains~'{safe_query}'"
                ")"
            )
        else:
            filter_expression = ""

        response = self._session.post(
            (f"{self.BASE_URL}/" "SalesDocuments/" "ReadToDataSourceResult"),
            data={
                "sort": "RequestDate-desc",
                "page": page,
                "pageSize": page_size,
                "group": "",
                "filter": filter_expression,
            },
            headers={
                "X-Requested-With": "XMLHttpRequest",
            },
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

        documents: list[PrefWebSalesDocumentSummary] = []

        for item in payload.get(
            "Data",
            [],
        ):
            documents.append(
                PrefWebSalesDocumentSummary(
                    row_id=item["RowId"],
                    number=int(item["PrefGestNumber"]),
                    alias_number=str(item["AliasNumber"]),
                    version=int(item["Version"]),
                    version_name=str(item["VersionName"]),
                    customer_code=(
                        str(item["CustomerCode"])
                        if item.get("CustomerCode") is not None
                        else None
                    ),
                    customer_name=str(item["CustomerName"]),
                    request_date=(item.get("RequestDate")),
                    shipping_work=(item.get("ShippingWork")),
                    user_name=(item.get("UserName")),
                    salesman_name=(item.get("SalesmanName")),
                    entity_name=(item.get("EntityName")),
                    remarks=(item.get("Remarks")),
                    reference=(item.get("Reference")),
                    customer_nif=(item.get("CustomerNif")),
                    customer_address=(item.get("CustomerAddress")),
                    customer_city=(item.get("CustomerCity")),
                    customer_country=(item.get("CustomerCountry")),
                    is_active=bool(item.get("IsActive")),
                    is_confirmed=bool(item.get("IsConfirmed")),
                    is_public=bool(item.get("IsPublic")),
                    subtotal=float(
                        item.get(
                            "Subtotal",
                            0,
                        )
                    ),
                    tax=float(
                        item.get(
                            "Tax",
                            0,
                        )
                    ),
                    final_price=float(
                        item.get(
                            "FinalPrice",
                            0,
                        )
                    ),
                    currency_symbol=(item.get("CurrencySymbolToPrint")),
                    currency_name=((item.get("PriceCurrency") or "").strip() or None),
                    has_order=bool(item.get("DocHasOrder")),
                    has_factory_version=bool(item.get("DocHasFactoryVersion")),
                )
            )

        return documents

    def get_versions(
        self,
        *,
        number: int,
    ) -> list[PrefWebDocumentVersion]:
        self.ensure_login()

        response = self._session.get(
            (f"{self.BASE_URL}/" "SalesDocuments/GetVersions"),
            params={
                "number": number,
            },
            headers={
                "X-Requested-With": ("XMLHttpRequest"),
            },
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

        return [
            PrefWebDocumentVersion(
                version=int(item["Version"]),
                version_name=str(item["VersionName"]),
                is_active=bool(item["IsActive"]),
            )
            for item in payload
        ]

    def get_sales_document_html(
        self,
        *,
        number: int,
        version: int,
    ) -> str:
        self.ensure_login()

        url = f"{self.BASE_URL}/" "SalesDocuments/Edit"

        response = self._session.get(
            url,
            params={
                "number": number,
                "version": version,
            },
            timeout=30,
            allow_redirects=True,
        )

        response.raise_for_status()

        html = response.text

        if self._looks_like_login_page(html):
            self._authenticated = False

            raise PrefWebAuthenticationError("PrefWeb session is not " "authenticated")

        if "CustomerName" not in html:
            raise RuntimeError("Unexpected PrefWeb sales " "document response")

        return html

    def _get_login_page(
        self,
    ) -> requests.Response:
        response = self._session.get(
            f"{self.BASE_URL}/",
            timeout=30,
        )

        response.raise_for_status()

        return response

    def _check_login(
        self,
    ) -> PrefWebLoginResult:
        response = self._session.post(
            (f"{self.BASE_URL}/" "Home/CheckLogin"),
            json={
                "email": self._email,
                "password": self._password,
            },
            headers={
                "Accept": "*/*",
                "Content-Type": ("application/json"),
                "X-Requested-With": ("XMLHttpRequest"),
                "Origin": ("https://www.prefweb.com"),
                "Referer": (f"{self.BASE_URL}/"),
            },
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

        entities = [
            PrefWebEntity(
                row_id=entity["RowId"],
                entity_id=entity["EntityId"],
                name=entity["Name"],
            )
            for entity in payload.get(
                "AvailableEntities",
                [],
            )
        ]

        result = PrefWebLoginResult(
            valid_login=bool(
                payload.get("ValidLogin"),
            ),
            error_message=payload.get("ErrorMessage"),
            available_entities=entities,
        )

        if not result.valid_login:
            raise PrefWebAuthenticationError(
                result.error_message or "PrefWeb login failed"
            )

        if not result.available_entities:
            raise PrefWebAuthenticationError(
                "PrefWeb returned no " "available entities"
            )

        return result

    def _select_entity(
        self,
        entities: list[PrefWebEntity],
    ) -> PrefWebEntity:
        if self._entity_id:
            requested = self._entity_id.lower()

            for entity in entities:
                if (
                    entity.row_id.lower() == requested
                    or entity.entity_id.lower() == requested
                ):
                    return entity

            raise PrefWebAuthenticationError(
                "Configured PREFWEB_ENTITY_ID " "is not available for this user"
            )

        if len(entities) == 1:
            return entities[0]

        raise PrefWebAuthenticationError(
            "Multiple PrefWeb entities are "
            "available. Configure "
            "PREFWEB_ENTITY_ID."
        )

    def _submit_login_form(
        self,
        *,
        form_action: str,
        verification_token: str,
        entity: PrefWebEntity,
    ) -> None:
        response = self._session.post(
            form_action,
            data={
                "__RequestVerificationToken": (verification_token),
                "Email": self._email,
                "Password": self._password,
                "EntityId": entity.row_id,
                "RememberMe": "false",
            },
            timeout=30,
            allow_redirects=True,
        )

        response.raise_for_status()

        if self._looks_like_login_page(response.text):
            raise PrefWebAuthenticationError(
                "PrefWeb credentials were "
                "validated but the final "
                "login form did not create "
                "an authenticated session"
            )

    def _extract_verification_token(
        self,
        html: str,
    ) -> str:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        token = soup.find(
            "input",
            attrs={"name": ("__RequestVerificationToken")},
        )

        if not isinstance(
            token,
            Tag,
        ):
            raise PrefWebAuthenticationError("Login verification token " "not found")

        value = token.get("value")

        if (
            not isinstance(
                value,
                str,
            )
            or not value
        ):
            raise PrefWebAuthenticationError("Login verification token " "has no value")

        return value

    def _extract_login_form_action(
        self,
        html: str,
    ) -> str:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        form = soup.find(
            "form",
            id="loginForm",
        )

        if not isinstance(
            form,
            Tag,
        ):
            raise PrefWebAuthenticationError("PrefWeb login form " "not found")

        action = form.get("action")

        if (
            not isinstance(
                action,
                str,
            )
            or not action
        ):
            raise PrefWebAuthenticationError("PrefWeb login form has " "no action")

        return urljoin(
            f"{self.BASE_URL}/",
            action,
        )

    @staticmethod
    def _looks_like_login_page(
        html: str,
    ) -> bool:
        return 'id="loginForm"' in html and "Home/CheckLogin" in html
