import warnings
from datetime import timedelta as TimeDelta
from typing import Optional

from cachelib.file import FileSystemCache
from flask import Flask

from .._utils import total_seconds
from ..base import ServerSideSession, ServerSideSessionInterface
from ..defaults import Defaults


class CacheLibSession(ServerSideSession):
    pass


class CacheLibSessionInterface(ServerSideSessionInterface):
    """Uses any :class:`cachelib` backend as a session storage.

    :param client: A :class:`cachelib` backend instance.
    :param key_prefix: A prefix that is added to storage keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param serialization_format: The serialization format to use for the session data.
    """

    session_class = CacheLibSession
    ttl = True

    def __init__(
        self,
        app: Flask = None,
        client: Optional[FileSystemCache] = Defaults.SESSION_CACHELIB,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_ID_LENGTH,
        serialization_format: str = Defaults.SESSION_SERIALIZATION_FORMAT,
    ):

        if client is None:
            warnings.warn(
                "No valid cachelib instance provided, attempting to create a new instance on localhost with default settings.",
                RuntimeWarning,
                stacklevel=1,
            )
            client = FileSystemCache("flask_session", threshold=500)

        self.cache = client

        super().__init__(
            None, key_prefix, use_signer, permanent, sid_length, serialization_format
        )

    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (item) from the database
        return self.cache.get(store_id)

    def _delete_session(self, store_id: str) -> None:
        self.cache.delete(store_id)

    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_time_to_live = total_seconds(session_lifetime)

        # Serialize the session data (or just cast into dictionary in this case)
        session_data = dict(session)

        # Update existing or create new session in the database
        self.cache.set(
            key=store_id,
            value=session_data,
            timeout=storage_time_to_live,
        )
