from pathlib import Path

from dotenv import load_dotenv

from backend.integrations.llm.gemini import (
    GeminiStructuredClient,
)
from backend.presentation.content.generator import (
    LLMPresentationContentGenerator,
)
from experiments.gemini_demo.manolo_spec import (
    spec,
)

load_dotenv(dotenv_path=Path(".env"))

generator = LLMPresentationContentGenerator(GeminiStructuredClient())

content = generator.generate(spec)

print()
print("=" * 80)
print("GEMINI GENERATED CONTENT")
print("=" * 80)
print()

print(content.model_dump_json(indent=2))
