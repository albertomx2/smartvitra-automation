from __future__ import annotations

import argparse
import time

from backend.db.session import (
    SessionLocal,
)
from backend.generation.runner import (
    GenerationJobRunner,
)


def run_once() -> bool:
    with SessionLocal() as db:
        return GenerationJobRunner(db).run_next()


def run_forever(
    *,
    poll_interval: float,
) -> None:
    print("SmartVitra generation " "worker started.")

    while True:
        processed = run_once()

        if not processed:
            time.sleep(poll_interval)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--once",
        action="store_true",
    )

    parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
    )

    args = parser.parse_args()

    if args.once:
        processed = run_once()

        print("Processed job:" f" {processed}")

        return

    run_forever(
        poll_interval=(args.poll_interval),
    )


if __name__ == "__main__":
    main()
