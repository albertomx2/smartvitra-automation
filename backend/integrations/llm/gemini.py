import json
import os
from typing import TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from backend.integrations.llm.models import (
    StructuredLLMClient,
)

T = TypeVar(
    "T",
    bound=BaseModel,
)


class GeminiStructuredClient(StructuredLLMClient):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        project_id: str | None = None,
        location: str | None = None,
        model: str | None = None,
    ) -> None:
        resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")
        resolved_project = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")

        if resolved_project:
            self._client = genai.Client(
                vertexai=True,
                project=resolved_project,
                location=(location or os.getenv("GOOGLE_CLOUD_LOCATION") or "global"),
            )
        elif resolved_api_key:
            self._client = genai.Client(api_key=resolved_api_key)
        else:
            raise ValueError("GOOGLE_CLOUD_PROJECT or GEMINI_API_KEY is required")

        resolved_model = model or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"

        self._model: str = resolved_model

    def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        # A structured response can occasionally be truncated by the model.
        # Retry only malformed/empty output once, before failing the whole
        # presentation. Transport/auth errors retain the SDK's own handling.
        for attempt in range(2):
            response = self._client.models.generate_content(
                model=self._model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=response_model,
                    max_output_tokens=8192 * (attempt + 1),
                    temperature=0.2,
                ),
            )

            if not response.text:
                if attempt == 0:
                    continue
                raise RuntimeError("Gemini returned no text after retry")

            try:
                payload = json.loads(response.text)
            except json.JSONDecodeError as exc:
                if attempt == 0:
                    continue
                raise RuntimeError("Gemini returned invalid JSON after retry") from exc

            return response_model.model_validate(payload)

        raise RuntimeError("Gemini returned no structured content")
