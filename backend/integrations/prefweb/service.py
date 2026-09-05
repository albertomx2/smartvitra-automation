from backend.integrations.prefweb.client import (
    PrefWebClient,
)
from backend.integrations.prefweb.models import (
    PrefWebDocumentVersion,
    PrefWebProject,
    PrefWebProjectWindow,
    PrefWebSalesDocumentSummary,
)
from backend.integrations.prefweb.parser import (
    PrefWebSalesDocumentParser,
)


class PrefWebService:
    def __init__(
        self,
        client: PrefWebClient | None = None,
    ) -> None:
        self._client = client or PrefWebClient()

        self._parser = PrefWebSalesDocumentParser()

    def login(
        self,
    ) -> None:
        self._client.ensure_login()

    def search_projects(
        self,
        *,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> list[PrefWebSalesDocumentSummary]:
        return self._client.search_sales_documents(
            query=query,
            page=page,
            page_size=page_size,
        )

    def get_versions(
        self,
        *,
        number: int,
    ) -> list[PrefWebDocumentVersion]:
        return self._client.get_versions(
            number=number,
        )

    def get_project_by_number(
        self,
        *,
        number: int,
        version: int,
    ) -> PrefWebProject:
        self._client.ensure_login()

        html = self._client.get_sales_document_html(
            number=number,
            version=version,
        )

        document = self._parser.parse(
            html,
        )

        summary = self._client.get_sales_document_summary(
            number=number,
            version=version,
        )

        if summary is not None:
            return self._build_project_from_summary(
                document=document,
                summary=summary,
            )

        return self._build_project_without_summary(
            document=document,
        )

    def get_window_svg(
        self,
        *,
        number: int,
        version: int,
        item_id: str,
    ) -> str:
        self._client.ensure_login()

        return self._client.get_sales_item_svg(
            number=number,
            version=version,
            item_id=item_id,
        )

    def _get_current_customer(
        self,
        *,
        document,
    ) -> dict:
        """Obtiene la ficha maestra actual del cliente de PrefWeb."""
        code = document.customer.code

        if not code:
            return {}

        return self._client.get_customer_for_sales_document(
            code=str(code),
            phone=document.customer.phone,
        )

    def get_project(
        self,
        *,
        summary: PrefWebSalesDocumentSummary,
    ) -> PrefWebProject:
        self._client.ensure_login()

        html = self._client.get_sales_document_html(
            number=summary.number,
            version=summary.version,
        )

        document = self._parser.parse(
            html,
        )

        return self._build_project_from_summary(
            document=document,
            summary=summary,
        )

    def _build_project_from_summary(
        self,
        *,
        document,
        summary: PrefWebSalesDocumentSummary,
    ) -> PrefWebProject:
        current_customer = self._get_current_customer(
            document=document,
        )

        discount_amount = float(document.commercial_discount_amount or 0)
        discount_percentage = document.commercial_discount_percentage

        return PrefWebProject(
            number=document.number,
            alias_number=(document.alias_number or summary.alias_number),
            version=document.version,
            version_name=(document.version_name or summary.version_name),
            customer_name=(current_customer.get("Name") or document.customer.name),
            customer_email=(current_customer.get("Email") or document.customer.email),
            customer_phone=(document.customer.mobile_phone or document.customer.phone),
            request_date=(document.request_date),
            reference=document.reference,
            payment_term=(document.payment_term),
            customer_address=(document.customer.address or summary.customer_address),
            customer_address2=(document.customer.address2),
            customer_postal_code=(document.customer.postal_code),
            customer_city=(document.customer.city or summary.customer_city),
            customer_country=(document.customer.country or summary.customer_country),
            subtotal=summary.subtotal,
            tax=summary.tax,
            final_price=summary.final_price,
            currency_symbol=(summary.currency_symbol or "€"),
            windows=[
                PrefWebProjectWindow(
                    id_pos=item.id_pos,
                    item_id=item.item_id,
                    position=(item.position or 0),
                    nomenclature=(item.nomenclature),
                    reference=item.reference,
                    description=(item.description),
                    color=item.color,
                    dimensions=(item.dimensions),
                    quantity=(item.quantity or 1),
                    total_amount=(item.total_amount or 0.0),
                    room=(item.internal_remarks),
                )
                for item in document.items
                if item.item_type == "Design"
            ],
            subtotal_before_discount=(
                document.subtotal_before_discount
                if document.subtotal_before_discount is not None
                else summary.subtotal + discount_amount
            ),
            discount_percentage=discount_percentage,
            discount_amount=discount_amount,
            has_discount=(discount_amount > 0 or float(discount_percentage or 0) > 0),
        )

    def _build_project_without_summary(
        self,
        *,
        document,
    ) -> PrefWebProject:
        subtotal_before_discount = (
            document.subtotal_before_discount
            if document.subtotal_before_discount is not None
            else sum(item.total_amount or 0 for item in document.items)
        )

        discount_amount = float(document.commercial_discount_amount or 0)

        subtotal = max(
            0.0,
            subtotal_before_discount - discount_amount,
        )

        tax = float(document.tax or 0)

        final_price = subtotal * (1 + tax / 100)

        current_customer = self._get_current_customer(
            document=document,
        )

        return PrefWebProject(
            number=document.number,
            alias_number=(document.alias_number or str(document.number)),
            version=document.version,
            version_name=(document.version_name or f"Versión {document.version}"),
            customer_name=(current_customer.get("Name") or document.customer.name),
            customer_email=(current_customer.get("Email") or document.customer.email),
            customer_phone=(document.customer.mobile_phone or document.customer.phone),
            request_date=(document.request_date),
            reference=document.reference,
            payment_term=(document.payment_term),
            customer_address=(document.customer.address),
            customer_address2=(document.customer.address2),
            customer_postal_code=(document.customer.postal_code),
            customer_city=(document.customer.city),
            customer_country=(document.customer.country),
            subtotal=subtotal,
            tax=tax,
            final_price=final_price,
            windows=[
                PrefWebProjectWindow(
                    id_pos=item.id_pos,
                    item_id=item.item_id,
                    position=(item.position or 0),
                    nomenclature=(item.nomenclature),
                    reference=item.reference,
                    description=(item.description),
                    color=item.color,
                    dimensions=(item.dimensions),
                    quantity=(item.quantity or 1),
                    total_amount=(item.total_amount or 0.0),
                    room=(item.internal_remarks),
                )
                for item in document.items
                if item.item_type == "Design"
            ],
            subtotal_before_discount=subtotal_before_discount,
            discount_percentage=(document.commercial_discount_percentage),
            discount_amount=discount_amount,
            has_discount=(
                discount_amount > 0
                or float(document.commercial_discount_percentage or 0) > 0
            ),
        )
