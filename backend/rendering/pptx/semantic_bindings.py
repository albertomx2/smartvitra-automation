from dataclasses import dataclass


@dataclass(frozen=True)
class SemanticCardBinding:
    outer_shape: str
    accent_shape: str


SEMANTIC_CARD_BINDINGS = {
    "s02_need_1": SemanticCardBinding(
        outer_shape="Rectángulo 3",
        accent_shape="Rectángulo 4",
    ),
    "s02_need_2": SemanticCardBinding(
        outer_shape="Rectángulo 7",
        accent_shape="Rectángulo 8",
    ),
    "s02_need_3": SemanticCardBinding(
        outer_shape="Rectángulo 5",
        accent_shape="Rectángulo 6",
    ),
    "s02_need_4": SemanticCardBinding(
        outer_shape="Rectángulo 9",
        accent_shape="Rectángulo 10",
    ),
}
