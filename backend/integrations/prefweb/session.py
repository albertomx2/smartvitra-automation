from __future__ import annotations

from threading import Lock

from backend.integrations.prefweb.client import PrefWebClient


class PrefWebSessionManager:
    """
    Manages one reusable authenticated PrefWeb session
    per SmartVitra backend process.

    The PrefWebClient itself is responsible for
    re-authenticating when the remote session expires.
    """

    def __init__(self) -> None:
        self._client: PrefWebClient | None = None
        self._lock = Lock()

    def get_client(self) -> PrefWebClient:
        if self._client is not None:
            return self._client

        with self._lock:
            if self._client is None:
                client = PrefWebClient()
                client.ensure_login()
                self._client = client

        return self._client

    def reset(self) -> None:
        with self._lock:
            self._client = None


prefweb_session_manager = PrefWebSessionManager()
