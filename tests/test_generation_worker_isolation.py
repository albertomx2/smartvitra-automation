from unittest.mock import Mock

import pytest

from backend.generation.runner import GenerationJobRunner


def test_cloud_run_configuration_cannot_poll_the_shared_queue(monkeypatch):
    monkeypatch.setenv("GENERATION_EXECUTION_BACKEND", "cloud_run")
    runner = GenerationJobRunner.__new__(GenerationJobRunner)
    runner._repository = Mock()

    with pytest.raises(RuntimeError, match="Queue polling is disabled"):
        runner.run_next()

    runner._repository.get_next_queued.assert_not_called()


def test_local_development_can_still_poll_a_local_queue(monkeypatch):
    monkeypatch.setenv("GENERATION_EXECUTION_BACKEND", "local")
    runner = GenerationJobRunner.__new__(GenerationJobRunner)
    runner._repository = Mock()
    runner._repository.get_next_queued.return_value = None

    assert runner.run_next() is False
    runner._repository.get_next_queued.assert_called_once_with()
