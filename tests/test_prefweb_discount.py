from types import SimpleNamespace

from backend.integrations.prefweb.parser import (
    PrefWebSalesDocumentParser,
)
from backend.integrations.prefweb.service import (
    PrefWebService,
)

DISCOUNTED_DOCUMENT_HTML = """
<html><body>
  <input id="Number" value="1000095703">
  <input id="Version" value="1">
  <input id="AliasNumber" value="2026/196">
  <input id="VersionName" value="Oferta">
  <input id="CustomerName" value="Cliente prueba">
  <input id="Tax" value="21">

  <input id="Item_IdPos_window-1" value="window-1">
  <input id="Item_ItemId_window-1" value="item-1">
  <input id="Item_Position_window-1" value="1">
  <input id="Item_Quantity_window-1" value="1">
  <input id="Item_PreciseUnitPrice_window-1" value="4354,09">
  <input id="Item_TotalAmount_window-1" value="4354,09">
  <input id="Item_ItemType_window-1" value="Design">

  <input id="Subtotal_Kind_4" value="5">
  <label id="Subtotal_Amount_4">4354,09</label>
  <input id="Subtotal_Kind_5" value="6">
  <input id="Subtotal_Percentage_5" value="15">
  <label id="Subtotal_Amount_5">653,11</label>
</body></html>
"""


def test_prefweb_parser_reads_document_commercial_discount() -> None:
    document = PrefWebSalesDocumentParser().parse(
        DISCOUNTED_DOCUMENT_HTML,
    )

    assert document.subtotal_before_discount == 4354.09
    assert document.commercial_discount_percentage == 15
    assert document.commercial_discount_amount == 653.11


def test_project_uses_authoritative_discounted_prefweb_totals() -> None:
    class FakeClient:
        def ensure_login(self) -> None:
            pass

        def get_sales_document_html(self, *, number: int, version: int) -> str:
            assert (number, version) == (1000095703, 1)
            return DISCOUNTED_DOCUMENT_HTML

        def get_sales_document_summary(self, *, number: int, version: int):
            return SimpleNamespace(
                alias_number="2026/196",
                version_name="Oferta",
                customer_address=None,
                customer_city=None,
                customer_country=None,
                subtotal=3700.98,
                tax=21.0,
                final_price=4478.19,
                currency_symbol="€",
            )

        def get_customer_for_sales_document(self, *, code: str, phone: str | None):
            raise AssertionError("No customer code was provided")

    project = PrefWebService(client=FakeClient()).get_project_by_number(
        number=1000095703,
        version=1,
    )

    assert project.subtotal_before_discount == 4354.09
    assert project.subtotal == 3700.98
    assert project.final_price == 4478.19
    assert project.discount_percentage == 15
    assert project.discount_amount == 653.11
    assert project.has_discount is True


def test_project_detects_design_line_discount_and_ignores_free_services() -> None:
    html = """
    <html><body>
      <input id="Number" value="1000095769">
      <input id="Version" value="1">
      <input id="AliasNumber" value="2026/198">
      <input id="CustomerName" value="Cliente prueba">
      <input id="Tax" value="21">
      <input id="Item_IdPos_window-1" value="window-1">
      <input id="Item_Position_window-1" value="1">
      <input id="Item_Quantity_window-1" value="1">
      <input id="Item_PreciseUnitPrice_window-1" value="1470,374115">
      <input id="Item_Discount_window-1" value="12">
      <input id="Item_TotalAmount_window-1" value="1293,93">
      <input id="Item_ItemType_window-1" value="Design">
      <input id="Item_IdPos_installation" value="installation">
      <input id="Item_Position_installation" value="2">
      <input id="Item_Quantity_installation" value="1">
      <input id="Item_PreciseUnitPrice_installation" value="180">
      <input id="Item_Discount_installation" value="100">
      <input id="Item_TotalAmount_installation" value="0">
      <input id="Item_ItemType_installation" value="Other">
    </body></html>
    """

    class FakeClient:
        def ensure_login(self) -> None:
            pass

        def get_sales_document_html(self, *, number: int, version: int) -> str:
            return html

        def get_sales_document_summary(self, *, number: int, version: int):
            return SimpleNamespace(
                alias_number="2026/198",
                version_name="Versión 1",
                customer_address=None,
                customer_city=None,
                customer_country=None,
                subtotal=1293.93,
                tax=21.0,
                final_price=1565.66,
                currency_symbol="€",
            )

        def get_customer_for_sales_document(self, *, code: str, phone: str | None):
            raise AssertionError("No customer code was provided")

    project = PrefWebService(client=FakeClient()).get_project_by_number(
        number=1000095769,
        version=1,
    )

    assert project.has_discount is True
    assert project.discount_percentage == 12
    assert round(project.discount_amount, 2) == 176.44
    assert round(project.subtotal_before_discount or 0, 2) == 1470.37
