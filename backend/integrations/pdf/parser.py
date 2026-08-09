import re
from datetime import date

from backend.integrations.pdf.models import (
    RawOpening,
    RawPaymentTerms,
    RawProposalData,
)
from backend.integrations.pdf.utils import parse_euro_decimal


class PdfProposalParser:
    def parse(self, text: str) -> RawProposalData:
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        proposal_number = self._value_after_label(
            lines,
            "Pedido nº",
        )

        proposal_date_raw = self._value_after_label(
            lines,
            "Fecha de pedido",
        )

        proposal_date = None

        if proposal_date_raw:
            day, month, year = proposal_date_raw.split("/")

            proposal_date = date(
                int(year),
                int(month),
                int(day),
            )

        commercial_name = self._value_after_label(
            lines,
            "Comercial",
        )

        customer_name = lines[0] if lines else None
        customer_address = lines[1] if len(lines) > 1 else None

        customer_city = None
        customer_country = None

        if len(lines) > 4:
            customer_city = lines[3]
            customer_country = lines[4]

        usual_cost = self._extract_amount_after_label(
            lines,
            "Coste habitual:",
        )

        discount_total = self._extract_amount_after_label(
            lines,
            "Descuentos:",
        )

        subtotal = self._extract_amount_after_label(
            lines,
            "Importe base",
        )

        tax_total = self._extract_amount_after_label(
            lines,
            "IVA 21%",
        )

        total = self._extract_amount_after_label(
            lines,
            "Total",
        )

        openings = self._extract_openings(lines)

        payment_terms = self._extract_payment_terms(lines)

        return RawProposalData(
            proposal_number=proposal_number,
            proposal_date=proposal_date,
            customer_name=customer_name,
            customer_address=customer_address,
            customer_city=customer_city,
            customer_country=customer_country,
            commercial_name=commercial_name,
            usual_cost=usual_cost,
            discount_total=discount_total,
            subtotal=subtotal,
            tax_total=tax_total,
            total=total,
            openings=openings,
            payment_terms=payment_terms,
            raw_text=text,
        )

    def _value_after_label(
        self,
        lines: list[str],
        label: str,
    ) -> str | None:
        try:
            index = lines.index(label)
        except ValueError:
            return None

        if index + 1 >= len(lines):
            return None

        return lines[index + 1]

    def _extract_amount_after_label(
        self,
        lines: list[str],
        label: str,
    ):
        value = self._value_after_label(
            lines,
            label,
        )

        if value is None:
            return None

        return parse_euro_decimal(value)

    def _extract_openings(
        self,
        lines: list[str],
    ) -> list[RawOpening]:
        openings: list[RawOpening] = []

        pattern = re.compile(
            r"^(?P<description>.+?) "
            r"Pos\. (?P<position>\d+) - "
            r"(?P<identifier>V\d+)\.$"
        )

        for index, line in enumerate(lines):
            match = pattern.match(line)

            if not match:
                continue

            room = None
            glass_description = None

            if index + 1 < len(lines):
                room = lines[index + 1]

            if index + 2 < len(lines):
                glass_description = lines[index + 2]

            openings.append(
                RawOpening(
                    position=int(match.group("position")),
                    identifier=match.group("identifier"),
                    description=match.group("description"),
                    room=room,
                    glass_description=glass_description,
                )
            )

        return openings

    def _extract_payment_terms(
        self,
        lines: list[str],
    ) -> RawPaymentTerms | None:
        try:
            start = lines.index("Términos de pago:")
        except ValueError:
            return None

        terms: list[str] = []

        for line in lines[start + 1 :]:
            if line.startswith("Comercial de Aluminio"):
                break

            terms.append(line)

        if not terms:
            return None

        return RawPaymentTerms(text=" ".join(terms))
