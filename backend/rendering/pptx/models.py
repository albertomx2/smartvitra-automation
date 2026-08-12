from enum import Enum

from pydantic import BaseModel


class SemanticColor(str, Enum):
    PROBLEM_HIGH = "problem_high"
    PROBLEM_MEDIUM = "problem_medium"
    POSITIVE = "positive"
    WARNING = "warning"
    NEUTRAL = "neutral"


class TextRenderResult(BaseModel):
    shape_name: str
    text: str

    estimated_too_long: bool = False
