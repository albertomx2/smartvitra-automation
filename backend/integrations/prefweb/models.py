from pydantic import BaseModel


class PrefWebEntity(BaseModel):
    row_id: str
    entity_id: str
    name: str


class PrefWebLoginResult(BaseModel):
    valid_login: bool
    error_message: str | None = None
    available_entities: list[PrefWebEntity]


class PrefWebCustomer(BaseModel):
    code: str | None = None
    name: str
    nif: str | None = None

    address: str | None = None
    address2: str | None = None

    postal_code: str | None = None
    city: str | None = None
    province: str | None = None
    country: str | None = None

    phone: str | None = None
    mobile_phone: str | None = None
    email: str | None = None


class PrefWebSalesItem(BaseModel):
    id_pos: str

    item_id: str | None = None

    position: int | None = None

    nomenclature: str | None = None
    reference: str | None = None
    description: str | None = None
    color: str | None = None
    dimensions: str | None = None

    quantity: int | None = None
    discount: float | None = None
    total_amount: float | None = None

    internal_remarks: str | None = None

    item_type: str | None = None
    item_subtype: str | None = None


class PrefWebSalesDocument(BaseModel):
    number: int
    version: int

    alias_number: str | None = None
    version_name: str | None = None

    request_date: str | None = None
    reference: str | None = None

    tariff_name: str | None = None
    payment_term: str | None = None
    tax: float | None = None

    customer: PrefWebCustomer

    items: list[PrefWebSalesItem]


class PrefWebSalesDocumentSummary(BaseModel):
    row_id: str

    number: int
    alias_number: str

    version: int
    version_name: str

    customer_code: str | None = None
    customer_name: str

    request_date: str | None = None

    shipping_work: str | None = None

    user_name: str | None = None
    salesman_name: str | None = None

    entity_name: str | None = None

    remarks: str | None = None
    reference: str | None = None

    customer_nif: str | None = None
    customer_address: str | None = None
    customer_address2: str | None = None
    customer_postal_code: str | None = None
    customer_city: str | None = None
    customer_country: str | None = None

    is_active: bool
    is_confirmed: bool
    is_public: bool

    subtotal: float
    tax: float
    final_price: float

    currency_symbol: str | None = None
    currency_name: str | None = None

    has_order: bool
    has_factory_version: bool


class PrefWebProjectWindow(BaseModel):
    id_pos: str
    item_id: str | None = None

    position: int
    nomenclature: str | None = None

    reference: str | None = None
    description: str | None = None
    color: str | None = None
    dimensions: str | None = None

    quantity: int
    total_amount: float

    room: str | None = None


class PrefWebProject(BaseModel):
    number: int
    alias_number: str

    version: int
    version_name: str

    customer_name: str

    request_date: str | None = None
    reference: str | None = None

    customer_address: str | None = None
    customer_address2: str | None = None
    customer_postal_code: str | None = None
    customer_city: str | None = None
    customer_country: str | None = None

    subtotal: float
    tax: float
    final_price: float

    currency_symbol: str = "€"

    windows: list[PrefWebProjectWindow]


class PrefWebDocumentVersion(BaseModel):
    version: int
    version_name: str
    is_active: bool
