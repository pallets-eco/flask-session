import warnings
from datetime import timedelta as TimeDelta
from typing import Optional

from cachelib.file import FileSystemCache
from flask import Flask

from .._utils import total_seconds
from ..base import ServerSideSession, ServerSideSessionInterface
from ..defaults import Defaults


class FileSystemSession(ServerSideSession):
    pass


class FileSystemSessionInterface(ServerSideSessionInterface):
    """Uses the :class:`cachelib.file.FileSystemCache` as a session storage.

    :param key_prefix: A prefix that is added to storage keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param serialization_format: The serialization format to use for the session data.
    :param cache_dir: the directory where session files are stored.
    :param threshold: the maximum number of items the session stores before it
    :param mode: the file mode wanted for the session files, default 0600

    .. versionadded:: 0.7
        The `serialization_format` and `app` parameters were added.

    .. versionadded:: 0.6
        The `sid_length` parameter was added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    session_class = FileSystemSession
    ttl = True

    def __init__(
        self,
        app: Flask,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_ID_LENGTH,
        serialization_format: str = Defaults.SESSION_SERIALIZATION_FORMAT,
        cache_dir: str = Defaults.SESSION_FILE_DIR,
        threshold: int = Defaults.SESSION_FILE_THRESHOLD,
        mode: int = Defaults.SESSION_FILE_MODE,
    ):

        # Deprecation warnings
        if cache_dir != Defaults.SESSION_FILE_DIR:
            warnings.warn(
                "'SESSION_FILE_DIR' is deprecated and will be removed in a future release. Instead pass FileSystemCache(directory, threshold, mode) instance as SESSION_CACHELIB.",
                DeprecationWarning,
                stacklevel=1,
            )
        if threshold != Defaults.SESSION_FILE_THRESHOLD:
            warnings.warn(
                "'SESSION_FILE_THRESHOLD' is deprecated and will be removed in a future release. Instead pass FileSystemCache(directory, threshold, mode) instance as SESSION_CLIENT.",
                DeprecationWarning,
                stacklevel=1,
            )
        if mode != Defaults.SESSION_FILE_MODE:
            warnings.warn(
                "'SESSION_FILE_MODE' is deprecated and will be removed in a future release. Instead pass FileSystemCache(directory, threshold, mode) instance as SESSION_CLIENT.",
                DeprecationWarning,
                stacklevel=1,
            )

        warnings.warn(
            "FileSystemSessionInterface is deprecated and will be removed in a future release. Instead use the CacheLib backend directly.",
            DeprecationWarning,
            stacklevel=1,
        )

        self.cache = FileSystemCache(
            cache_dir=cache_dir, threshold=threshold, mode=mode
        )

        super().__init__(
            app, key_prefix, use_signer, permanent, sid_length, serialization_format
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
