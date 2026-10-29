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
        response = self._client.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=(system_prompt),
                response_mime_type=("application/json"),
                response_schema=(response_model),
                temperature=0.2,
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned no text")

        try:
            payload = json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Gemini returned invalid JSON") from exc

        return response_model.model_validate(payload)
