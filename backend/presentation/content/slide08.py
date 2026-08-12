from pydantic import BaseModel


class Slide08Content(BaseModel):
    before_text: str
    after_text: str
