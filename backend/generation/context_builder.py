from __future__ import annotations

from backend.generation.snapshot import (
    CaseGenerationSnapshot,
)

PROBLEM_DEFINITIONS = {
    "noise": {
        "code": "acoustic_noise",
        "description": ("El cliente quiere mejorar " "el aislamiento acústico."),
    },
    "thermal": {
        "code": "thermal_insulation",
        "description": ("El cliente quiere mejorar " "el aislamiento térmico."),
    },
    "air": {
        "code": "air_tightness",
        "description": ("El cliente detecta " "corrientes o infiltraciones de aire."),
    },
    "security": {
        "code": "security",
        "description": (
            "El cliente quiere mejorar " "la seguridad de los cerramientos."
        ),
    },
    "aesthetic": {
        "code": "aesthetics",
        "description": (
            "El cliente quiere mejorar " "la estética de los cerramientos."
        ),
    },
    "other": {
        "code": "other",
        "description": ("El cliente ha indicado " "una necesidad adicional."),
    },
}


class GenerationContextBuilder:
    def build(
        self,
        snapshot: CaseGenerationSnapshot,
    ) -> dict:
        needs = []

        priority = 5

        for window in snapshot.windows:
            if not window.problem_type:
                continue

            definition = PROBLEM_DEFINITIONS.get(
                window.problem_type,
            )

            if definition is None:
                continue

            source_parts: list[str] = []

            if window.room:
                source_parts.append(f"Estancia: {window.room}.")

            if window.commercial_notes:
                source_parts.append(window.commercial_notes)

            needs.append(
                {
                    "code": definition["code"],
                    "priority": max(
                        priority,
                        1,
                    ),
                    "description": (definition["description"]),
                    "source_text": (" ".join(source_parts) or None),
                    "opening_id": (window.prefweb_item_id),
                }
            )

            priority -= 1

        if snapshot.visit_notes:
            needs.append(
                {
                    "code": "visit_context",
                    "priority": 2,
                    "description": (
                        "Información adicional " "recogida durante la visita."
                    ),
                    "source_text": (snapshot.visit_notes),
                }
            )

        openings = []

        for window in snapshot.windows:
            openings.append(
                {
                    "opening_id": (window.prefweb_item_id),
                    "position": (window.position),
                    "nomenclature": (window.nomenclature),
                    "room": window.room,
                    "window_type": (window.description),
                    "reference": (window.reference),
                    "color": window.color,
                    "dimensions": (window.dimensions),
                    "quantity": (window.quantity),
                    "amount": (window.total_amount),
                    "commercial_notes": (window.commercial_notes),
                }
            )

        return {
            "customer": {
                "name": (snapshot.project.customer_name),
                "address": (snapshot.project.customer_address),
                "address2": (snapshot.project.customer_address2),
                "postal_code": (snapshot.project.customer_postal_code),
                "city": (snapshot.project.customer_city),
                "country": (snapshot.project.customer_country),
            },
            "visit_notes": (snapshot.visit_notes),
            "needs": needs,
            "proposal": {
                "openings": openings,
                # Product catalogue/matching will be
                # connected in the next vertical slice.
                # Empty means: do not invent technical
                # product claims.
                "products": [],
                "services": [],
            },
            "pricing": {
                "subtotal": (snapshot.project.subtotal),
                "tax_percentage": (snapshot.project.tax),
                "total": (snapshot.project.final_price),
                "currency": (snapshot.project.currency_symbol),
            },
        }
