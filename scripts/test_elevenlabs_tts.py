from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.elevenlabs.client import (
    ElevenLabsClient,
)

VOICE_ID = "SIKGLxQDD9IQ2ip3wCI1"

TEXT = "Hola, esta es una prueba breve " "de la voz de SmartVitra."


def main() -> None:
    load_dotenv(
        dotenv_path=Path(".env"),
    )

    client = ElevenLabsClient()

    before = client.get_subscription()

    before_count = int(
        getattr(
            before,
            "character_count",
            0,
        )
        or 0
    )

    print(
        "Créditos usados antes:",
        before_count,
    )

    result = client.generate_speech(
        text=TEXT,
        voice_id=VOICE_ID,
        output_path=Path("tmp/elevenlabs/" "smartvitra_voice_test.mp3"),
    )

    after = client.get_subscription()

    after_count = int(
        getattr(
            after,
            "character_count",
            0,
        )
        or 0
    )

    consumed = after_count - before_count

    print()
    print("Texto:")
    print(TEXT)

    print()
    print(
        "Caracteres enviados:",
        result.characters,
    )

    print(
        "Créditos usados después:",
        after_count,
    )

    print(
        "Créditos consumidos:",
        consumed,
    )

    print(
        "Archivo:",
        result.output_path,
    )

    print(
        "Bytes:",
        result.output_path.stat().st_size,
    )


if __name__ == "__main__":
    main()
