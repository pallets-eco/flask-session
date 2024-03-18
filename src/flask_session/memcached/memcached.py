import time
import warnings
from datetime import timedelta as TimeDelta
from typing import Any, Optional, Protocol

from flask import Flask

from .._utils import total_seconds
from ..base import ServerSideSession, ServerSideSessionInterface
from ..defaults import Defaults


class MemcacheClientProtocol(Protocol):
    def get(self, key: str) -> Optional[Any]: ...
    def set(self, key: str, value: Any, timeout: int) -> bool: ...
    def delete(self, key: str) -> bool: ...


class MemcachedSession(ServerSideSession):
    pass


class MemcachedSessionInterface(ServerSideSessionInterface):
    """A Session interface that uses memcached as session storage. (`pylibmc`, `libmc`, `python-memcached` or `pymemcache` required)

    :param client: A ``memcache.Client`` instance.
    :param key_prefix: A prefix that is added to all storage keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param serialization_format: The serialization format to use for the session data.

    .. versionadded:: 0.7
        The `serialization_format` and `app` parameters were added.

    .. versionadded:: 0.6
        The `sid_length` parameter was added.

    .. versionadded:: 0.2
        The `use_signer` parameter was added.
    """

    serializer = ServerSideSessionInterface.serializer
    session_class = MemcachedSession
    ttl = True

    def __init__(
        self,
        app: Flask,
        client: Optional[MemcacheClientProtocol] = Defaults.SESSION_MEMCACHED,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_ID_LENGTH,
        serialization_format: str = Defaults.SESSION_SERIALIZATION_FORMAT,
    ):
        if client is None or not all(
            hasattr(client, method) for method in ["get", "set", "delete"]
        ):
            warnings.warn(
                "No valid memcache.Client instance provided, attempting to create a new instance on localhost with default settings.",
                RuntimeWarning,
                stacklevel=1,
            )
            client = self._get_preferred_memcache_client()
        self.client = client
        super().__init__(
            app, key_prefix, use_signer, permanent, sid_length, serialization_format
        )

    def _get_preferred_memcache_client(self):
        clients = [
            ("pylibmc", ["127.0.0.1:11211"]),
            ("memcache", ["127.0.0.1:11211"]),  # python-memcached
            ("pymemcache.client.base", "127.0.0.1:11211"),
            ("libmc", ["localhost:11211"]),
        ]

        for module_name, server in clients:
            try:
                module = __import__(module_name)
                ClientClass = module.Client
                return ClientClass(server)
            except ImportError:
                continue

        raise ImportError("No memcache module found")

    def _get_memcache_timeout(self, timeout: int) -> int:
        """
        Memcached deals with long (> 30 days) timeouts in a special
        way. Call this function to obtain a safe value for your timeout.
        """
        if timeout > 2592000:  # 60*60*24*30, 30 days
            # Switch to absolute timestamps.
            timeout += int(time.time())
        return timeout

    def _retrieve_session_data(self, store_id: str) -> Optional[dict]:
        # Get the saved session (item) from the database
        serialized_session_data = self.client.get(store_id)
        if serialized_session_data:
            return self.serializer.decode(serialized_session_data)
        return None

    def _delete_session(self, store_id: str) -> None:
        self.client.delete(store_id)

    def _upsert_session(
        self, session_lifetime: TimeDelta, session: ServerSideSession, store_id: str
    ) -> None:
        storage_time_to_live = total_seconds(session_lifetime)

        # Serialize the session data
        serialized_session_data = self.serializer.encode(session)

        # Update existing or create new session in the database
        self.client.set(
            store_id,
            serialized_session_data,
            self._get_memcache_timeout(storage_time_to_live),
        )
