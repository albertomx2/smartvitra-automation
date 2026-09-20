from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from backend.integrations.prefweb.models import PrefWebProject, PrefWebSalesItem

CENT = Decimal("0.01")


def _money(value: float) -> Decimal:
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def _line_title(item: PrefWebSalesItem) -> str:
    title = (
        item.description or item.reference or item.nomenclature or "Partida PrefWeb"
    ).strip()
    if item.item_type == "Design" and item.position is not None:
        position = f"Pos. {item.position}"
        if position.lower() not in title.lower():
            title = f"{title} {position}"
        if item.nomenclature and item.nomenclature.lower() not in title.lower():
            title = f"{title} - {item.nomenclature.strip()}"
    return title


def validate_prefweb_quote_totals(project: PrefWebProject) -> None:
    if not project.items:
        raise ValueError("PrefWeb document has no sale items")
    source_subtotal = Decimal(0)
    for item in project.items:
        amount = _money(item.total_amount or 0)
        if item.unit_price is None and amount != 0:
            raise ValueError(f"PrefWeb item {item.id_pos} has no unit price")
        source_subtotal += amount

    expected_subtotal = source_subtotal - _money(
        abs(project.commercial_discount_amount)
    )
    if abs(expected_subtotal - _money(project.subtotal)) > Decimal("0.02"):
        raise ValueError(
            "PrefWeb line totals do not match its authoritative subtotal; "
            "Odoo quotation was not created"
        )


def build_sale_order_lines(
    project: PrefWebProject,
    *,
    goods_tax_id: int,
    services_tax_id: int,
    product_id: int,
    product_uom_id: int,
) -> list[dict[str, Any]]:
    """Mirror every PrefWeb item, including included services, without repricing it."""
    validate_prefweb_quote_totals(project)

    lines: list[dict[str, Any]] = []
    for index, item in enumerate(project.items, start=1):
        quantity = item.quantity or 1
        tax_id = goods_tax_id if item.item_type == "Design" else services_tax_id
        lines.append(
            {
                "sequence": index * 10,
                "name": _line_title(item),
                "product_id": product_id,
                "product_uom_id": product_uom_id,
                "product_uom_qty": quantity,
                "price_unit": float(item.unit_price or 0),
                "discount": float(item.discount or 0),
                "tax_ids": [[6, 0, [tax_id] if tax_id else []]],
            }
        )

    header_discount = _money(abs(project.commercial_discount_amount))
    if header_discount:
        lines.append(
            {
                "sequence": (len(lines) + 1) * 10,
                "name": "Descuento comercial PrefWeb",
                "product_id": product_id,
                "product_uom_id": product_uom_id,
                "product_uom_qty": 1,
                "price_unit": -float(header_discount),
                "discount": 0,
                "tax_ids": [[6, 0, [goods_tax_id] if goods_tax_id else []]],
            }
        )
    return lines
