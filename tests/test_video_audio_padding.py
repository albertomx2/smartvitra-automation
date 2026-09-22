from pathlib import Path

import pytest

from backend.generation.video.renderer import (
    NarratedPresentationVideoRenderer,
)


def test_video_renderer_requires_audio_for_all_ten_slides(
    tmp_path: Path,
) -> None:
    renderer = NarratedPresentationVideoRenderer()

    with pytest.raises(
        ValueError,
        match="Exactly 10 slide audio files are required",
    ):
        renderer.render(
            presentation_path=tmp_path / "presentation.pptx",
            slide_audio_paths=[
                tmp_path / f"slide_{index:02d}.mp3" for index in range(1, 10)
            ],
            output_video_path=tmp_path / "video.mp4",
            output_audio_path=tmp_path / "audio.mp3",
            work_dir=tmp_path,
        )


def test_slide_audio_gets_a_safe_silent_tail(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source = tmp_path / "source.mp3"
    output = tmp_path / "padded.mp3"
    source.write_bytes(b"audio")

    command: list[str] = []

    monkeypatch.setattr(
        NarratedPresentationVideoRenderer,
        "_require_binary",
        lambda name: None,
    )

    def fake_run(args, **kwargs):
        command.extend(args)
        Path(args[-1]).write_bytes(b"padded-audio")

    monkeypatch.setattr(
        "backend.generation.video.renderer.subprocess.run",
        fake_run,
    )

    result = NarratedPresentationVideoRenderer.add_slide_end_padding(
        source_path=source,
        output_path=output,
    )

    assert result == output
    assert output.read_bytes() == b"padded-audio"
    assert (
        f"apad=pad_dur="
        f"{NarratedPresentationVideoRenderer.SLIDE_END_PADDING_SECONDS}" in command
    )
