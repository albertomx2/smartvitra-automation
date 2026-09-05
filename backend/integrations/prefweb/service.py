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

        (
            discount_amount,
            discount_percentage,
            subtotal_before_discount,
        ) = self._effective_discount(
            document=document,
            subtotal=summary.subtotal,
        )

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
                    unit_price=item.unit_price,
                    discount=item.discount,
                    total_amount=(item.total_amount or 0.0),
                    room=(item.internal_remarks),
                )
                for item in document.items
                if item.item_type == "Design"
            ],
            subtotal_before_discount=subtotal_before_discount,
            discount_percentage=discount_percentage,
            discount_amount=discount_amount,
            has_discount=(discount_amount > 0 or float(discount_percentage or 0) > 0),
        )

    def _build_project_without_summary(
        self,
        *,
        document,
    ) -> PrefWebProject:
        item_subtotal = sum(item.total_amount or 0 for item in document.items)
        (
            discount_amount,
            discount_percentage,
            subtotal_before_discount,
        ) = self._effective_discount(
            document=document,
            subtotal=item_subtotal,
        )

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
                    unit_price=item.unit_price,
                    discount=item.discount,
                    total_amount=(item.total_amount or 0.0),
                    room=(item.internal_remarks),
                )
                for item in document.items
                if item.item_type == "Design"
            ],
            subtotal_before_discount=subtotal_before_discount,
            discount_percentage=discount_percentage,
            discount_amount=discount_amount,
            has_discount=(discount_amount > 0 or float(discount_percentage or 0) > 0),
        )

    @staticmethod
    def _effective_discount(
        *,
        document,
        subtotal: float,
    ) -> tuple[float, float | None, float]:
        """Combine real window-line and document commercial discounts.

        Free ancillary rows (for example installation at 100%) are deliberately
        excluded: the customer-facing promotion is the discount applied to the
        designed windows.
        """

        design_items = [item for item in document.items if item.item_type == "Design"]
        line_gross = sum(
            float(item.unit_price or 0) * float(item.quantity or 1)
            for item in design_items
            if float(item.discount or 0) > 0
        )
        line_net = sum(
            float(item.total_amount or 0)
            for item in design_items
            if float(item.discount or 0) > 0
        )
        line_discount_amount = max(0.0, line_gross - line_net)

        commercial_amount = abs(float(document.commercial_discount_amount or 0))
        total_discount_amount = line_discount_amount + commercial_amount

        base = subtotal + total_discount_amount
        percentage = (
            round((total_discount_amount / base) * 100, 2)
            if total_discount_amount > 0 and base > 0
            else None
        )

        if line_discount_amount == 0 and document.commercial_discount_percentage:
            percentage = float(document.commercial_discount_percentage)

        subtotal_before_discount = (
            float(document.subtotal_before_discount) + line_discount_amount
            if document.subtotal_before_discount is not None
            else base
        )

        return total_discount_amount, percentage, subtotal_before_discount
