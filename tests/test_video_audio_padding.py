from pathlib import Path

from backend.generation.video.renderer import (
    NarratedPresentationVideoRenderer,
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
