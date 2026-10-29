from backend.integrations.llm.gemini import GeminiStructuredClient


def test_gemini_client_prefers_vertex_in_cloud(monkeypatch) -> None:
    calls: list[dict] = []

    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "smartvitra-project")
    monkeypatch.setenv("GEMINI_API_KEY", "free-tier-key")
    monkeypatch.setattr(
        "backend.integrations.llm.gemini.genai.Client",
        lambda **kwargs: calls.append(kwargs) or object(),
    )

    GeminiStructuredClient()

    assert calls == [
        {
            "vertexai": True,
            "project": "smartvitra-project",
            "location": "global",
        }
    ]


def test_gemini_client_keeps_api_key_fallback(monkeypatch) -> None:
    calls: list[dict] = []

    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    monkeypatch.setattr(
        "backend.integrations.llm.gemini.genai.Client",
        lambda **kwargs: calls.append(kwargs) or object(),
    )

    GeminiStructuredClient(api_key="local-key")

    assert calls == [{"api_key": "local-key"}]
