from typing import Literal

from pydantic import BaseModel


class RewriteTextAction(BaseModel):
    action: Literal["rewrite_text"] = "rewrite_text"

    shape_name: str

    instruction: str

    max_characters: int


class SetSemanticColorAction(BaseModel):
    action: Literal["set_semantic_color"] = "set_semantic_color"

    shape_name: str

    semantic_color: str


class HideShapeAction(BaseModel):
    action: Literal["hide_shape"] = "hide_shape"

    shape_name: str
