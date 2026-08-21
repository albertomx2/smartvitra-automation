from __future__ import annotations

import os
from pathlib import Path

import requests


class ElevenLabsNarrationGenerator:
    API_BASE_URL = "https://api.elevenlabs.io/v1/" "text-to-speech"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        voice_id: str | None = None,
        model_id: str | None = None,
    ) -> None:
        self._api_key = api_key or os.getenv("ELEVENLABS_API_KEY") or ""

        self._voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID") or ""

        self._model_id = (
            model_id or os.getenv("ELEVENLABS_MODEL") or "eleven_multilingual_v2"
        )

        if not self._api_key:
            raise ValueError("ELEVENLABS_API_KEY is required")

        if not self._voice_id:
            raise ValueError("ELEVENLABS_VOICE_ID is required")

    def generate(
        self,
        *,
        text: str,
        output_path: Path,
    ) -> Path:
        cleaned = text.strip()

        if not cleaned:
            raise ValueError("Narration text cannot be empty")

        response = requests.post(
            (f"{self.API_BASE_URL}/" f"{self._voice_id}"),
            params={
                "output_format": "mp3_44100_128",
            },
            headers={
                "xi-api-key": self._api_key,
                "Content-Type": "application/json",
            },
            json={
                "text": cleaned,
                "model_id": self._model_id,
                "voice_settings": {
                    "stability": 0.45,
                    "similarity_boost": 0.85,
                    "style": 0.20,
                    "use_speaker_boost": True,
                    "speed": 0.98,
                },
            },
            timeout=120,
        )

        if not response.ok:
            raise RuntimeError(
                "ElevenLabs TTS failed: "
                f"HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )

        if not response.content:
            raise RuntimeError("ElevenLabs returned empty audio")

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_bytes(response.content)

        return output_path
