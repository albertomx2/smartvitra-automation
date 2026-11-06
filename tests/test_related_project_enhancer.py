from pathlib import Path
from unittest.mock import Mock

import pytest
from PIL import Image

from backend.reference_photos.image_enhancer import RelatedProjectImageEnhancer


def test_reference_edit_is_cached_and_original_is_unchanged(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    source = tmp_path / "source.jpg"
    Image.new("RGB", (90, 120), "navy").save(source)
    original = source.read_bytes()
    requests = []

    class FakeClient:
        DEFAULT_MODEL = "test-image-model"

        def __init__(self, **kwargs):
            pass

        def generate(self, **kwargs):
            requests.append(kwargs)
            Image.new("RGB", (90, 120), "white").save(kwargs["output_path"])

    monkeypatch.setattr(
        "backend.reference_photos.image_enhancer.VertexSolutionImageClient", FakeClient
    )
    enhancer = RelatedProjectImageEnhancer(cache_root=tmp_path / "cache")
    first = enhancer.enhance(source_photo=source)
    second = enhancer.enhance(source_photo=source)

    assert first == second
    assert source.read_bytes() == original
    assert len(requests) == 1
    assert requests[0]["source_photo"] == source
    assert requests[0]["aspect_ratio"] == "3:4"
    assert "window_reference" not in requests[0]
    assert "fully finished" in requests[0]["prompt"]
    assert "adult person" in requests[0]["prompt"]


def test_cloud_cache_reuses_edit_without_requesting_gemini(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "r2")
    source = tmp_path / "source.jpg"
    Image.new("RGB", (90, 120), "navy").save(source)

    class FakeR2:
        def exists(self, **kwargs):
            return True

        def download_file(self, *, storage_key: str, destination: Path):
            destination.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (90, 120), "white").save(destination)

    client = Mock()
    monkeypatch.setattr(
        "backend.reference_photos.image_enhancer.R2StorageClient", FakeR2
    )
    monkeypatch.setattr(
        "backend.reference_photos.image_enhancer.VertexSolutionImageClient.generate",
        client,
    )

    result = RelatedProjectImageEnhancer(cache_root=tmp_path / "cache").enhance(
        source_photo=source
    )

    assert result.exists()
    client.assert_not_called()


def test_invalid_generated_image_never_falls_back_to_the_original(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    source = tmp_path / "source.jpg"
    Image.new("RGB", (90, 120), "navy").save(source)
    monkeypatch.setattr(
        "backend.reference_photos.image_enhancer.VertexSolutionImageClient.__init__",
        lambda self, **kwargs: None,
    )
    monkeypatch.setattr(
        "backend.reference_photos.image_enhancer.VertexSolutionImageClient.generate",
        lambda self, **kwargs: kwargs["output_path"].write_bytes(b"invalid"),
    )

    with pytest.raises(RuntimeError, match="invalid related-project image"):
        RelatedProjectImageEnhancer(cache_root=tmp_path / "cache").enhance(
            source_photo=source
        )
