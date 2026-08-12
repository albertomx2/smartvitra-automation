from pydantic import BaseModel


class RoomWindowSummary(BaseModel):
    label: str

    quantity: int


class RoomsTableContent(BaseModel):
    rows: list[RoomWindowSummary]

    total_quantity: int
