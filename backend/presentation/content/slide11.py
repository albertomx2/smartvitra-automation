from typing import Literal

from pydantic import BaseModel


class Slide11Content(BaseModel):
    tip_text: str

    tip_icon_key: Literal[
        "durability",
        "maintenance",
        "energy",
        "thermal",
        "comfort",
        "security",
    ]
