from __future__ import annotations

import argparse

from dotenv import load_dotenv

from backend.generation.narration.elevenlabs import (
    ElevenLabsNarrationGenerator,
)
from backend.generation.narration.script.fixed import (
    FIXED_NARRATION_TEXT,
    FIXED_NARRATION_VOICE_ID,
    fixed_audio_path,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate SmartVitra's versioned fixed narration assets once.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing MP3 assets after intentionally changing fixed copy.",
    )
    parser.add_argument(
        "--voice-id",
        default=FIXED_NARRATION_VOICE_ID,
        help="ElevenLabs voice ID; defaults to the versioned SmartVitra voice.",
    )
    args = parser.parse_args()

    load_dotenv()
    generator = ElevenLabsNarrationGenerator(
        voice_id=args.voice_id,
    )

    for slide_number, text in FIXED_NARRATION_TEXT.items():
        output_path = fixed_audio_path(slide_number)

        if output_path.exists() and not args.force:
            print(f"slide {slide_number}: already exists")
            continue

        generator.generate(
            text=text,
            output_path=output_path,
        )
        print(f"slide {slide_number}: generated {output_path}")


if __name__ == "__main__":
    main()
