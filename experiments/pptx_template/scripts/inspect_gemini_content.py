from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.llm.gemini import (
    GeminiStructuredClient,
)
from backend.presentation.content.generator import (
    LLMPresentationContentGenerator,
)
from scripts.inspect_presentation_spec import (
    spec,
)

load_dotenv(dotenv_path=Path(".env"))

client = GeminiStructuredClient()

generator = LLMPresentationContentGenerator(client)

content = generator.generate(spec)

print(content.model_dump_json(indent=2))
