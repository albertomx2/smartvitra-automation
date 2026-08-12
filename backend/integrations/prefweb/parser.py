import re

from bs4 import BeautifulSoup
from bs4.element import Tag

from backend.integrations.prefweb.models import (
    PrefWebCustomer,
    PrefWebSalesDocument,
    PrefWebSalesItem,
)

ITEM_ID_PATTERN = re.compile(r"^Item_IdPos_(?P<id_pos>.+)$")


class PrefWebSalesDocumentParser:
    def parse(
        self,
        html: str,
    ) -> PrefWebSalesDocument:
        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        number = self._required_int(
            soup,
            "Number",
        )

        version = self._required_int(
            soup,
            "Version",
        )

        customer = PrefWebCustomer(
            code=self._value(
                soup,
                "CustomerCode",
            ),
            name=(
                self._value(
                    soup,
                    "CustomerName",
                )
                or ""
            ),
            nif=self._value(
                soup,
                "CustomerNif",
            ),
            address=self._value(
                soup,
                "CustomerAddress",
            ),
            address2=self._value(
                soup,
                "CustomerAddress2",
            ),
            postal_code=self._value(
                soup,
                "CustomerPostalCode",
            ),
            city=self._value(
                soup,
                "CustomerCity",
            ),
            province=self._value(
                soup,
                "CustomerProvince",
            ),
            country=self._value(
                soup,
                "CustomerCountry",
            ),
            phone=self._value(
                soup,
                "CustomerPhone",
            ),
            mobile_phone=self._value(
                soup,
                "CustomerMobilePhone",
            ),
            email=self._value(
                soup,
                "CustomerEmail",
            ),
        )

        items = self._parse_items(
            soup,
        )

        return PrefWebSalesDocument(
            number=number,
            version=version,
            alias_number=self._value(
                soup,
                "AliasNumber",
            ),
            version_name=self._value(
                soup,
                "VersionName",
            ),
            request_date=self._value(
                soup,
                "RequestDate",
            ),
            reference=self._value(
                soup,
                "Reference",
            ),
            tariff_name=self._value(
                soup,
                "TariffName",
            ),
            payment_term=self._value(
                soup,
                "PaymentTerm",
            ),
            tax=self._parse_float(
                self._value(
                    soup,
                    "Tax",
                ),
            ),
            customer=customer,
            items=items,
        )

    def _parse_items(
        self,
        soup: BeautifulSoup,
    ) -> list[PrefWebSalesItem]:
        ids: list[str] = []

        for element in soup.find_all(
            id=ITEM_ID_PATTERN,
        ):
            if not isinstance(
                element,
                Tag,
            ):
                continue

            element_id = element.get(
                "id",
            )

            if not isinstance(
                element_id,
                str,
            ):
                continue

            match = ITEM_ID_PATTERN.match(
                element_id,
            )

            if match is None:
                continue

            ids.append(
                match.group("id_pos"),
            )

        items: list[PrefWebSalesItem] = []

        for id_pos in ids:
            items.append(
                PrefWebSalesItem(
                    id_pos=id_pos,
                    item_id=self._value(
                        soup,
                        f"Item_ItemId_{id_pos}",
                    ),
                    position=self._parse_int(
                        self._value(
                            soup,
                            f"Item_Position_{id_pos}",
                        ),
                    ),
                    nomenclature=self._value(
                        soup,
                        f"Item_Nomenclature_{id_pos}",
                    ),
                    reference=self._value(
                        soup,
                        f"Item_Reference_{id_pos}",
                    ),
                    description=self._value(
                        soup,
                        f"Item_Description_{id_pos}",
                    ),
                    color=self._value(
                        soup,
                        f"Item_Color_{id_pos}",
                    ),
                    dimensions=self._value(
                        soup,
                        f"Item_Dimensions_{id_pos}",
                    ),
                    quantity=self._parse_int(
                        self._value(
                            soup,
                            f"Item_Quantity_{id_pos}",
                        ),
                    ),
                    discount=self._parse_float(
                        self._value(
                            soup,
                            f"Item_Discount_{id_pos}",
                        ),
                    ),
                    total_amount=self._parse_float(
                        self._value(
                            soup,
                            f"Item_TotalAmount_{id_pos}",
                        ),
                    ),
                    internal_remarks=self._value(
                        soup,
                        f"Item_InternalRemarks_{id_pos}",
                    ),
                    item_type=self._value(
                        soup,
                        f"Item_ItemType_{id_pos}",
                    ),
                    item_subtype=self._value(
                        soup,
                        f"Item_ItemSubType_{id_pos}",
                    ),
                )
            )

        return sorted(
            items,
            key=lambda item: (item.position if item.position is not None else 999999),
        )

    @staticmethod
    def _value(
        soup: BeautifulSoup,
        element_id: str,
    ) -> str | None:
        element = soup.find(
            id=element_id,
        )

        if element is None:
            element = soup.find(
                name=None,
                attrs={
                    "name": element_id,
                },
            )

        if not isinstance(
            element,
            Tag,
        ):
            return None

        if element.name == "textarea":
            value = element.get_text(
                strip=True,
            )

            return value or None

        raw_value = element.get(
            "value",
        )

        if isinstance(
            raw_value,
            str,
        ):
            value = raw_value.strip()

            return value or None

        text = element.get_text(
            strip=True,
        )

        return text or None

    def _required_int(
        self,
        soup: BeautifulSoup,
        element_id: str,
    ) -> int:
        value = self._value(
            soup,
            element_id,
        )

        parsed = self._parse_int(
            value,
        )

        if parsed is None:
            raise ValueError(f"Missing or invalid field: {element_id}")

        return parsed

    @staticmethod
    def _parse_int(
        value: str | None,
    ) -> int | None:
        if value is None:
            return None

        cleaned = value.strip()

        if not cleaned:
            return None

        try:
            return int(
                cleaned,
            )
        except ValueError:
            return None

    @staticmethod
    def _parse_float(
        value: str | None,
    ) -> float | None:
        if value is None:
            return None

        cleaned = value.strip().replace("€", "").replace(" ", "")

        if not cleaned:
            return None

        if "," in cleaned:
            cleaned = cleaned.replace(
                ".",
                "",
            )

            cleaned = cleaned.replace(
                ",",
                ".",
            )

        try:
            return float(
                cleaned,
            )
        except ValueError:
            return None
