import re
from datetime import date
from decimal import InvalidOperation

from backend.integrations.pdf.models import (
    RawAdvancePayment,
    RawDiscountLine,
    RawOpening,
    RawPaymentTerms,
    RawProposalData,
    RawServiceLine,
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

        services = self._extract_services(lines)

        discounts = self._extract_discounts(lines)

        advance_payments = self._extract_advance_payments(lines)

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
            services=services,
            discounts=discounts,
            advance_payments=advance_payments,
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

            try:
                room = lines[index + 1]
                glass_description = lines[index + 2]

                quantity = parse_euro_decimal(lines[index + 3])

                list_price = parse_euro_decimal(lines[index + 5])

                discounted_unit_price = parse_euro_decimal(lines[index + 7])

                discount_percentage = parse_euro_decimal(lines[index + 9])

                tax_match = re.match(
                    r"(?P<tax>\d+(?:,\d+)?)%",
                    lines[index + 10],
                )

                tax_percentage = None

                if tax_match:
                    tax_percentage = parse_euro_decimal(tax_match.group("tax"))

                subtotal = parse_euro_decimal(lines[index + 11])

            except (
                IndexError,
                ValueError,
            ):
                quantity = None
                list_price = None
                discounted_unit_price = None
                discount_percentage = None
                tax_percentage = None
                subtotal = None

            openings.append(
                RawOpening(
                    position=int(match.group("position")),
                    identifier=match.group("identifier"),
                    description=match.group("description"),
                    room=room,
                    glass_description=(glass_description),
                    quantity=quantity,
                    list_price=list_price,
                    discounted_unit_price=(discounted_unit_price),
                    discount_percentage=(discount_percentage),
                    tax_percentage=tax_percentage,
                    subtotal=subtotal,
                )
            )

        return openings

    def _extract_services(
        self,
        lines: list[str],
    ) -> list[RawServiceLine]:
        services: list[RawServiceLine] = []

        service_names = (
            "INSTALACIÓN INCLUIDA",
            "EXTRA ALBAÑILERÍA",
        )

        for service_name in service_names:
            try:
                start = lines.index(service_name)
            except ValueError:
                continue

            quantity_index = None

            for index in range(
                start + 1,
                min(start + 25, len(lines)),
            ):
                if index + 1 < len(lines) and lines[index + 1].lower() == "unidades":
                    quantity_index = index
                    break

            if quantity_index is None:
                continue

            quantity = parse_euro_decimal(lines[quantity_index])

            list_price = parse_euro_decimal(lines[quantity_index + 2])

            discounted_unit_price = parse_euro_decimal(lines[quantity_index + 4])

            discount_percentage = parse_euro_decimal(lines[quantity_index + 6])

            tax_match = re.match(
                r"(?P<tax>\d+(?:,\d+)?)%",
                lines[quantity_index + 7],
            )

            tax_percentage = None

            if tax_match:
                tax_percentage = parse_euro_decimal(tax_match.group("tax"))

            subtotal = parse_euro_decimal(lines[quantity_index + 8])

            description_lines = lines[start + 1 : quantity_index]

            services.append(
                RawServiceLine(
                    name=service_name,
                    description=" ".join(description_lines),
                    quantity=quantity,
                    list_price=list_price,
                    discounted_unit_price=(discounted_unit_price),
                    discount_percentage=(discount_percentage),
                    tax_percentage=tax_percentage,
                    subtotal=subtotal,
                )
            )

        return services

    def _extract_discounts(
        self,
        lines: list[str],
    ):
        discounts = []

        for index, line in enumerate(lines):
            if not line.startswith("EXTRA COMERCIAL DEL"):
                continue

            amount = None

            for candidate in lines[index + 1 : min(index + 12, len(lines))]:
                try:
                    parsed = parse_euro_decimal(candidate)
                except InvalidOperation:
                    continue

                if parsed < 0:
                    amount = parsed
                    break

            discounts.append(
                RawDiscountLine(
                    name=line,
                    amount=amount,
                )
            )

        return discounts

    def _extract_advance_payments(
        self,
        lines: list[str],
    ) -> list[RawAdvancePayment]:
        payments: list[RawAdvancePayment] = []

        pattern = re.compile(
            r"^Anticipo \(ref: "
            r"(?P<reference>.+?) el "
            r"(?P<date>\d{2}/\d{2}/\d{4})\)$"
        )

        for index, line in enumerate(lines):
            match = pattern.match(line)

            if not match:
                continue

            day, month, year = match.group("date").split("/")

            payment_date = date(
                int(year),
                int(month),
                int(day),
            )

            amount = None

            for candidate in lines[index + 1 : min(index + 8, len(lines))]:
                try:
                    parsed = parse_euro_decimal(candidate)
                except InvalidOperation:
                    continue

                if parsed > 0:
                    amount = parsed
                    break

            payments.append(
                RawAdvancePayment(
                    reference=match.group("reference"),
                    payment_date=payment_date,
                    amount=amount,
                )
            )

        return payments

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
