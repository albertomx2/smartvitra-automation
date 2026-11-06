from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from backend.integrations.llm.gemini import GeminiStructuredClient


class StructuredResponse(BaseModel):
    status: str


@pytest.mark.parametrize("first_text", ['{"status": "incomplet', None])
def test_structured_generation_recovers_once_from_incomplete_output(first_text):
    generate = Mock(
        side_effect=[
            SimpleNamespace(text=first_text),
            SimpleNamespace(text='{"status":"ok"}'),
        ]
    )
    client = GeminiStructuredClient.__new__(GeminiStructuredClient)
    client._client = SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    client._model = "test-model"

    response = client.generate_structured(
        system_prompt="test", user_prompt="test", response_model=StructuredResponse
    )

    assert response.status == "ok"
    assert generate.call_count == 2
    assert (
        generate.call_args_list[1].kwargs["config"].max_output_tokens
        > generate.call_args_list[0].kwargs["config"].max_output_tokens
    )


def test_malformed_output_retries_are_bounded():
    generate = Mock(return_value=SimpleNamespace(text='{"status": "incomplet'))
    client = GeminiStructuredClient.__new__(GeminiStructuredClient)
    client._client = SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    client._model = "test-model"

    with pytest.raises(RuntimeError, match="invalid JSON after retry"):
        client.generate_structured(
            system_prompt="test", user_prompt="test", response_model=StructuredResponse
        )

    assert generate.call_count == 2
