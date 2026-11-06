from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PIL import Image

from backend.integrations.image_generation.vertex import VertexSolutionImageClient


@pytest.mark.parametrize("with_reference", [True, False])
def test_vertex_supports_both_window_reference_and_single_photo_editing(
    tmp_path, with_reference
):
    source = tmp_path / "source.png"
    Image.new("RGB", (90, 120), "navy").save(source)
    response = SimpleNamespace(
        candidates=[
            SimpleNamespace(
                content=SimpleNamespace(
                    parts=[
                        SimpleNamespace(
                            inline_data=SimpleNamespace(data=source.read_bytes())
                        )
                    ]
                )
            )
        ]
    )
    generate = Mock(return_value=response)
    client = VertexSolutionImageClient.__new__(VertexSolutionImageClient)
    client._client = SimpleNamespace(models=SimpleNamespace(generate_content=generate))
    client._model = "test-model"
    output = tmp_path / "result.png"

    client.generate(
        source_photo=source,
        window_reference=source if with_reference else None,
        prompt="Preserve the window and finish the room.",
        output_path=output,
        aspect_ratio=None if with_reference else "3:4",
    )

    request = generate.call_args.kwargs
    assert len(request["contents"].parts) == (3 if with_reference else 2)
    if with_reference:
        assert request["config"].image_config is None
    else:
        assert request["config"].image_config.aspect_ratio == "3:4"
    assert output.read_bytes() == source.read_bytes()
