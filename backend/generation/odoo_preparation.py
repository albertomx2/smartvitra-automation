from __future__ import annotations

import logging
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from backend.cases.repository import CaseRepository
from backend.cases.service import ProjectCaseService
from backend.db.models.generation import GenerationArtifact, GenerationJob
from backend.generation.artifact_repository import GenerationArtifactRepository
from backend.integrations.odoo import OdooClient
from backend.integrations.odoo.quotation import (
    build_sale_order_lines,
    validate_prefweb_quote_totals,
)
from backend.integrations.prefweb.service import PrefWebService
from backend.storage.generated import GeneratedFileStorage

logger = logging.getLogger(__name__)


class OdooQuotationPreparationService:
    """Create a draft Odoo quotation before launching expensive generation."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def prepare(
        self, *, job: GenerationJob, overwrite_odoo_quote_id: int | None = None
    ) -> None:
        case = CaseRepository(self._db).get(case_id=job.case_id)
        if case is None:
            raise LookupError("Project case not found")

        prefweb = PrefWebService()
        project = prefweb.get_project_by_number(
            number=case.prefweb_number,
            version=case.prefweb_version,
        )
        email = (project.customer_email or "").strip()
        if not email:
            raise ValueError(
                "PrefWeb customer needs an email to create an Odoo contact"
            )

        case = ProjectCaseService(
            self._db, prefweb_service=prefweb
        ).sync_windows_from_prefweb(case=case, project=project)

        validate_prefweb_quote_totals(project)
        expected_total = (
            Decimal(str(project.subtotal))
            * (Decimal(1) + Decimal(str(project.tax)) / Decimal(100))
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if abs(expected_total - Decimal(str(project.final_price))) > Decimal("0.02"):
            raise ValueError("PrefWeb subtotal, tax and final price are inconsistent")

        odoo = OdooClient()
        goods_tax_id, services_tax_id = odoo.get_sale_tax_ids(rate=project.tax)
        product_id, product_uom_id = odoo.ensure_prefweb_line_product()
        lines = build_sale_order_lines(
            project,
            goods_tax_id=goods_tax_id,
            services_tax_id=services_tax_id,
            product_id=product_id,
            product_uom_id=product_uom_id,
        )

        partner, created = odoo.find_or_create_partner(
            name=project.customer_name,
            email=email,
            phone=project.customer_phone,
            street=project.customer_address,
            street2=project.customer_address2,
            postal_code=project.customer_postal_code,
            city=project.customer_city,
        )
        partner_id = int(partner["id"])
        origin = f"SmartVitra generation {job.id}"
        reference = project.reference or project.alias_number
        if overwrite_odoo_quote_id is not None:
            quote = odoo.update_sale_quote(
                quote_id=overwrite_odoo_quote_id,
                partner_id=partner_id,
                origin=origin,
                reference=reference,
                prefweb_number=project.alias_number,
                payment_term=project.payment_term,
                lines=lines,
            )
        else:
            quote = odoo.create_sale_quote(
                partner_id=partner_id,
                origin=origin,
                reference=reference,
                prefweb_number=project.alias_number,
                payment_term=project.payment_term,
                lines=lines,
            )
        if abs(
            Decimal(str(quote["amount_total"])) - Decimal(str(project.final_price))
        ) > Decimal("0.05"):
            raise ValueError(
                "Odoo quotation total does not match PrefWeb; "
                f"review draft {quote['name']} before generation"
            )

        job.odoo_partner_id = partner_id
        job.odoo_partner_created = created
        job.odoo_sale_order_id = int(quote["id"])
        job.odoo_sale_order_name = str(quote["name"])
        self._db.commit()

        # The quote is useful even when its optional PDF cannot be rendered.
        try:
            pdf = odoo.fetch_sale_quote_pdf(quote_id=job.odoo_sale_order_id)
            storage = GeneratedFileStorage()
            work_dir = storage.build_job_directory(case_id=case.id, job_id=job.id)
            filename = f"Presupuesto_Odoo_{job.odoo_sale_order_name}.pdf"
            path = work_dir / filename
            path.write_bytes(pdf)
            storage_key = storage.persist(path=path, content_type="application/pdf")
            GenerationArtifactRepository(self._db).add(
                GenerationArtifact(
                    generation_job_id=job.id,
                    kind="odoo_quote",
                    filename=filename,
                    storage_key=storage_key,
                    content_type="application/pdf",
                    size_bytes=len(pdf),
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Odoo quotation PDF unavailable for generation %s: %s",
                job.id,
                type(exc).__name__,
            )
