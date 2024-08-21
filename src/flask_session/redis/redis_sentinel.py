from typing import Optional

from flask import Flask
from redis import Sentinel

from .redis import RedisSessionInterface
from ..base import ServerSideSession
from ..defaults import Defaults


class RedisSentinelSession(ServerSideSession):
    pass


class RedisSentinelSessionInterface(RedisSessionInterface):
    """Uses the Redis key-value store deployed in a high availability mode as a session storage. (`redis-py` required)

    :param client: A ``redis.Sentinel`` instance.
    :param master: The name of the master node.
    :param key_prefix: A prefix that is added to all storage keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    :param sid_length: The length of the generated session id in bytes.
    :param serialization_format: The serialization format to use for the session data.
    """

    session_class = RedisSentinelSession
    ttl = True

    def __init__(
        self,
        app: Flask,
        client: Optional[Sentinel] = Defaults.SESSION_REDIS_SENTINEL,
        master: str = Defaults.SESSION_REDIS_SENTINEL_MASTER_SET,
        key_prefix: str = Defaults.SESSION_KEY_PREFIX,
        use_signer: bool = Defaults.SESSION_USE_SIGNER,
        permanent: bool = Defaults.SESSION_PERMANENT,
        sid_length: int = Defaults.SESSION_ID_LENGTH,
        serialization_format: str = Defaults.SESSION_SERIALIZATION_FORMAT,
    ):
        if client is None or not isinstance(client, Sentinel):
            raise TypeError("No valid Sentinel instance provided.")
        self.sentinel = client
        self.master = master
        super().__init__(
            app, self.client, key_prefix, use_signer, permanent, sid_length, serialization_format
        )
        self._client = None

    @property
    def client(self):
        return self.sentinel.master_for(self.master)
    
    @client.setter
    def client(self, value):
        # the _client is only needed and the setter only needed for the inheritance to work
        self._client = value
