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

        return PrefWebProject(
            number=document.number,
            alias_number=(document.alias_number or summary.alias_number),
            version=document.version,
            version_name=(document.version_name or summary.version_name),
            customer_name=(document.customer.name),
            request_date=(document.request_date),
            reference=document.reference,
            customer_address=(document.customer.address or summary.customer_address),
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
        )

    @staticmethod
    def _build_project_without_summary(
        *,
        document,
    ) -> PrefWebProject:
        subtotal = sum(item.total_amount for item in document.items)

        tax = float(document.tax or 0)

        final_price = subtotal * (1 + tax / 100)

        return PrefWebProject(
            number=document.number,
            alias_number=(document.alias_number or str(document.number)),
            version=document.version,
            version_name=(document.version_name or f"Versión {document.version}"),
            customer_name=(document.customer.name),
            request_date=(document.request_date),
            reference=document.reference,
            customer_address=(document.customer.address),
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
        )
