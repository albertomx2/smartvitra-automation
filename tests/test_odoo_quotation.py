import uuid
from types import SimpleNamespace

import pytest

from backend.api import generation as generation_api
from backend.cases.proposal_status import classify_proposal_status
from backend.integrations.odoo.client import OdooClient
from backend.integrations.odoo.quotation import build_sale_order_lines
from backend.integrations.prefweb.models import PrefWebProject, PrefWebSalesItem


def _project(*, subtotal: float = 1253.73) -> PrefWebProject:
    return PrefWebProject(
        number=1000095769,
        alias_number="2026/198",
        version=1,
        version_name="Versión 1",
        customer_name="Cliente prueba",
        subtotal=subtotal,
        tax=21,
        final_price=1517.01,
        windows=[],
        items=[
            PrefWebSalesItem(
                id_pos="window",
                position=1,
                nomenclature="V1.",
                description="Corredera 2 hojas",
                item_type="Design",
                quantity=1,
                unit_price=1424.691608,
                discount=12,
                total_amount=1253.73,
            ),
            PrefWebSalesItem(
                id_pos="installation",
                position=2,
                description="Instalación incluida",
                item_type="Other",
                quantity=1,
                unit_price=180,
                discount=100,
                total_amount=0,
            ),
        ],
    )


def test_sale_quote_mirrors_prefweb_prices_and_included_services() -> None:
    lines = build_sale_order_lines(
        _project(),
        goods_tax_id=1,
        services_tax_id=2,
        product_id=9,
        product_uom_id=1,
    )
    assert len(lines) == 2
    assert lines[0]["name"] == "Corredera 2 hojas Pos. 1 - V1."
    assert lines[0]["price_unit"] == 1424.691608
    assert lines[0]["product_id"] == 9
    assert lines[0]["product_uom_id"] == 1
    assert lines[0]["discount"] == 12
    assert lines[0]["tax_ids"] == [[6, 0, [1]]]
    assert lines[1]["discount"] == 100
    assert lines[1]["tax_ids"] == [[6, 0, [2]]]


def test_sale_quote_adds_only_document_level_discount() -> None:
    project = _project(subtotal=1153.73)
    project.commercial_discount_amount = 100
    lines = build_sale_order_lines(
        project,
        goods_tax_id=1,
        services_tax_id=2,
        product_id=9,
        product_uom_id=1,
    )
    assert len(lines) == 3
    assert lines[-1]["price_unit"] == -100
    assert lines[0]["discount"] == 12


def test_sale_quote_rejects_inconsistent_prefweb_totals() -> None:
    with pytest.raises(ValueError, match="authoritative subtotal"):
        build_sale_order_lines(
            _project(subtotal=1000),
            goods_tax_id=1,
            services_tax_id=2,
            product_id=9,
            product_uom_id=1,
        )


@pytest.mark.parametrize(
    ("case_exists", "job_status", "sent", "expected"),
    [
        (False, None, False, "not_started"),
        (True, None, False, "draft_in_progress"),
        (True, "queued", False, "draft_in_progress"),
        (True, "failed", False, "draft_in_progress"),
        (True, "completed", False, "generated"),
        (True, "completed", True, "sent"),
    ],
)
def test_proposal_statuses(
    case_exists: bool, job_status: str | None, sent: bool, expected: str
) -> None:
    assert (
        classify_proposal_status(
            case_exists=case_exists, job_status=job_status, sent=sent
        )
        == expected
    )


def test_odoo_quote_creation_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OdooClient(base_url="https://odoo.example", api_key="test")
    calls: list[tuple[str, dict]] = []
    quote = {
        "id": 42,
        "name": "S00042",
        "state": "draft",
        "partner_id": [7, "Cliente"],
        "amount_total": 1517.01,
    }

    def fake_request(*, model: str, method: str, payload: dict, timeout=30):
        calls.append((method, payload))
        if method == "search_read":
            return [quote] if any(name == "create" for name, _ in calls) else []
        if method == "create":
            return 42
        raise AssertionError(method)

    monkeypatch.setattr(client, "_request", fake_request)
    result = client.create_sale_quote(
        partner_id=7,
        origin="SmartVitra generation test",
        reference="PrefWeb 2026/198",
        prefweb_number="2026/198",
        payment_term=None,
        lines=[{"name": "Ventana"}],
    )
    assert result == quote
    assert calls[1][1]["vals_list"]["order_line"] == [[0, 0, {"name": "Ventana"}]]
    assert calls[1][1]["vals_list"]["x_studio_no_presupuesto_preweb"] == "2026/198"

    calls.clear()
    monkeypatch.setattr(
        client,
        "find_sale_quote_by_origin",
        lambda *, origin: quote,
    )
    assert (
        client.create_sale_quote(
            partner_id=7,
            origin="SmartVitra generation test",
            reference="PrefWeb 2026/198",
            prefweb_number="2026/198",
            payment_term=None,
            lines=[],
        )
        == quote
    )
    assert calls == []


def test_odoo_reuses_one_technical_product(monkeypatch: pytest.MonkeyPatch) -> None:
    client = OdooClient(base_url="https://odoo.example", api_key="test")
    calls: list[str] = []

    def fake_request(*, model: str, method: str, payload: dict, timeout=30):
        assert model == "product.product"
        calls.append(method)
        return [{"id": 9, "uom_id": [1, "Units"]}]

    monkeypatch.setattr(client, "_request", fake_request)
    assert client.ensure_prefweb_line_product() == (9, 1)
    assert calls == ["search_read"]


def test_odoo_quote_pdf_uses_scoped_portal_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = OdooClient(base_url="https://odoo.example", api_key="test")
    monkeypatch.setattr(
        client,
        "_request",
        lambda **kwargs: "/my/orders/42?access_token=token",
    )
    calls: list[dict] = []

    def fake_get(url: str, **kwargs: object) -> SimpleNamespace:
        calls.append({"url": url, **kwargs})
        return SimpleNamespace(
            status_code=200,
            headers={"Content-Type": "application/pdf"},
            content=b"%PDF-1.7 example",
        )

    monkeypatch.setattr("backend.integrations.odoo.client.requests.get", fake_get)
    assert client.fetch_sale_quote_pdf(quote_id=42).startswith(b"%PDF-")
    assert calls[0]["params"] == {"report_type": "pdf", "download": "true"}
    assert calls[0]["allow_redirects"] is False
    assert "Authorization" not in calls[0]["headers"]


def test_odoo_quote_pdf_rejects_foreign_host_and_html(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = OdooClient(base_url="https://odoo.example", api_key="test")
    monkeypatch.setattr(client, "_request", lambda **kwargs: "https://evil.example/pdf")
    with pytest.raises(RuntimeError, match="unexpected host"):
        client.fetch_sale_quote_pdf(quote_id=42)

    monkeypatch.setattr(client, "_request", lambda **kwargs: "/my/orders/42")
    monkeypatch.setattr(
        "backend.integrations.odoo.client.requests.get",
        lambda *args, **kwargs: SimpleNamespace(
            status_code=200,
            headers={"Content-Type": "text/html"},
            content=b"<html>Login</html>",
        ),
    )
    with pytest.raises(RuntimeError, match="PDF unavailable"):
        client.fetch_sale_quote_pdf(quote_id=42)


def test_generate_prepares_odoo_before_launch(monkeypatch: pytest.MonkeyPatch) -> None:
    events: list[str] = []
    job = SimpleNamespace(id=uuid.uuid4())

    class FakeGenerationJobService:
        def __init__(self, db: object) -> None:
            pass

        def create_job(self, *, case_id: uuid.UUID):
            events.append("create_job")
            return job

    class FakeOdooPreparation:
        def __init__(self, db: object) -> None:
            pass

        def prepare(self, *, job: object) -> None:
            events.append("prepare_odoo")

    class FakeLauncher:
        def launch(self, *, job_id: uuid.UUID) -> None:
            events.append("launch_generation")

    monkeypatch.setattr(
        generation_api, "GenerationJobService", FakeGenerationJobService
    )
    monkeypatch.setattr(
        generation_api, "OdooQuotationPreparationService", FakeOdooPreparation
    )
    monkeypatch.setattr(generation_api, "GenerationLauncher", FakeLauncher)
    monkeypatch.setattr(generation_api, "_to_read", lambda job, db: job)

    assert generation_api.create_generation_job(uuid.uuid4(), object()) is job
    assert events == ["create_job", "prepare_odoo", "launch_generation"]
