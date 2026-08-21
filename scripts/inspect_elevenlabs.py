from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.elevenlabs.client import (
    ElevenLabsClient,
)

load_dotenv(
    dotenv_path=Path(".env"),
)


def main() -> None:
    client = ElevenLabsClient()

    subscription = client.get_subscription()

    print("=" * 70)
    print("ELEVENLABS SUBSCRIPTION")
    print("=" * 70)

    print(
        "tier:",
        getattr(
            subscription,
            "tier",
            None,
        ),
    )

    print(
        "status:",
        getattr(
            subscription,
            "status",
            None,
        ),
    )

    print(
        "character_count:",
        getattr(
            subscription,
            "character_count",
            None,
        ),
    )

    print(
        "character_limit:",
        getattr(
            subscription,
            "character_limit",
            None,
        ),
    )

    print(
        "next_reset:",
        getattr(
            subscription,
            "next_character_count_reset_unix",
            None,
        ),
    )

    print()
    print("=" * 70)
    print("VOICES")
    print("=" * 70)

    response = client.get_voices()

    voices = getattr(
        response,
        "voices",
        [],
    )

    for voice in voices:
        print()
        print(
            "name:",
            getattr(
                voice,
                "name",
                None,
            ),
        )
        print(
            "voice_id:",
            getattr(
                voice,
                "voice_id",
                None,
            ),
        )
        print(
            "category:",
            getattr(
                voice,
                "category",
                None,
            ),
        )


if __name__ == "__main__":
    main()
