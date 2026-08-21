from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from elevenlabs.client import ElevenLabs


@dataclass(frozen=True)
class SpeechGenerationResult:
    output_path: Path
    characters: int


class ElevenLabsClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
    ) -> None:
        resolved_api_key = api_key or os.getenv("ELEVENLABS_API_KEY") or ""

        if not resolved_api_key:
            raise ValueError("ELEVENLABS_API_KEY is required")

        self._client = ElevenLabs(
            api_key=resolved_api_key,
        )

    def get_subscription(self):
        return self._client.user.subscription.get()

    def get_voices(self):
        return self._client.voices.get_all()

    def generate_speech(
        self,
        *,
        text: str,
        voice_id: str,
        output_path: Path,
        model_id: str = "eleven_multilingual_v2",
    ) -> SpeechGenerationResult:
        clean_text = text.strip()

        if not clean_text:
            raise ValueError("Speech text cannot be empty")

        audio = self._client.text_to_speech.convert(
            voice_id=voice_id,
            text=clean_text,
            model_id=model_id,
            output_format="mp3_44100_128",
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open("wb") as file:
            for chunk in audio:
                if chunk:
                    file.write(chunk)

        if not output_path.exists():
            raise RuntimeError("ElevenLabs did not create audio output")

        if output_path.stat().st_size == 0:
            raise RuntimeError("ElevenLabs returned empty audio")

        return SpeechGenerationResult(
            output_path=output_path,
            characters=len(clean_text),
        )
