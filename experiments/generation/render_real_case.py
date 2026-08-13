from __future__ import annotations

import uuid
from pathlib import Path

from backend.db.session import SessionLocal
from backend.generation.context_builder import GenerationContextBuilder
from backend.generation.presentation import RealPresentationGenerator
from backend.generation.snapshot_builder import GenerationSnapshotBuilder


CASE_ID = uuid.UUID(
    "10376604-2c48-4649-b5c1-438a3cf736ca"
)

OUTPUT = Path(
    "tmp/real_generation/"
    "SmartVitra_REAL_2026-189.pptx"
)

WORK_DIR = Path(
    "tmp/real_generation/work"
)


def main() -> None:
    print("=" * 80)
    print("BUILDING REAL SNAPSHOT")
    print("=" * 80)

    with SessionLocal() as db:
        snapshot = GenerationSnapshotBuilder(
            db
        ).build(
            case_id=CASE_ID,
        )

        context = GenerationContextBuilder().build(
            snapshot
        )

    print(
        f"Cliente: "
        f"{snapshot.project.customer_name}"
    )
    print(
        f"Presupuesto: "
        f"{snapshot.project.alias_number}"
    )
    print(
        f"Ventanas: "
        f"{len(snapshot.windows)}"
    )
    print(
        f"Precio final: "
        f"{snapshot.project.final_price}"
    )

    print()
    print("=" * 80)
    print("GENERATING REAL PRESENTATION")
    print("=" * 80)

    generator = RealPresentationGenerator()

    result = generator.generate(
        snapshot=snapshot,
        context=context,
        output_path=OUTPUT,
        work_dir=WORK_DIR,
    )

    print()
    print("=" * 80)
    print("REAL PPTX CREATED")
    print("=" * 80)
    print(result)


if __name__ == "__main__":
    main()
