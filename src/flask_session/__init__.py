from .defaults import Defaults

__version__ = "0.8.0"


class Session:
    """This class is used to add Server-side Session to one or more Flask
    applications.

    :param app: A Flask app instance.

    For a typical setup use the following initialization::

        app = Flask(__name__)
        Session(app)

    .. note::

        You can not use ``Session`` instance directly, what ``Session`` does
        is just change the :attr:`~flask.Flask.session_interface` attribute on
        your Flask applications. You should always use :class:`flask.session`.
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """This the the alternate setup method, typically used in an application factory pattern::

            sess = Session()

            def create_app():
                app = Flask(__name__)
                sess.init_app(app)
                return app

        :param app: the Flask app object with proper configuration.
        """
        app.session_interface = self._get_interface(app)

    def _get_interface(self, app):
        config = app.config

        # Flask-session specific settings
        SESSION_TYPE = config.get("SESSION_TYPE", Defaults.SESSION_TYPE)

        SESSION_PERMANENT = config.get("SESSION_PERMANENT", Defaults.SESSION_PERMANENT)
        SESSION_USE_SIGNER = config.get(
            "SESSION_USE_SIGNER", Defaults.SESSION_USE_SIGNER
        )  # TODO: remove in 1.0
        SESSION_KEY_PREFIX = config.get(
            "SESSION_KEY_PREFIX", Defaults.SESSION_KEY_PREFIX
        )
        SESSION_ID_LENGTH = config.get("SESSION_ID_LENGTH", Defaults.SESSION_ID_LENGTH)
        SESSION_SERIALIZATION_FORMAT = config.get(
            "SESSION_SERIALIZATION_FORMAT", Defaults.SESSION_SERIALIZATION_FORMAT
        )

        # Redis settings
        SESSION_REDIS = config.get("SESSION_REDIS", Defaults.SESSION_REDIS)

        # Memcached settings
        SESSION_MEMCACHED = config.get("SESSION_MEMCACHED", Defaults.SESSION_MEMCACHED)

        # CacheLib settings
        SESSION_CACHELIB = config.get("SESSION_CACHELIB", Defaults.SESSION_CACHELIB)

        # Filesystem settings
        # TODO: remove in 1.0
        SESSION_FILE_DIR = config.get("SESSION_FILE_DIR", Defaults.SESSION_FILE_DIR)
        SESSION_FILE_THRESHOLD = config.get(
            "SESSION_FILE_THRESHOLD", Defaults.SESSION_FILE_THRESHOLD
        )
        SESSION_FILE_MODE = config.get("SESSION_FILE_MODE", Defaults.SESSION_FILE_MODE)

        # MongoDB settings
        SESSION_MONGODB = config.get("SESSION_MONGODB", Defaults.SESSION_MONGODB)
        SESSION_MONGODB_DB = config.get(
            "SESSION_MONGODB_DB", Defaults.SESSION_MONGODB_DB
        )
        SESSION_MONGODB_COLLECT = config.get(
            "SESSION_MONGODB_COLLECT", Defaults.SESSION_MONGODB_COLLECT
        )

        # SQLAlchemy settings
        SESSION_SQLALCHEMY = config.get(
            "SESSION_SQLALCHEMY", Defaults.SESSION_SQLALCHEMY
        )
        SESSION_SQLALCHEMY_TABLE = config.get(
            "SESSION_SQLALCHEMY_TABLE", Defaults.SESSION_SQLALCHEMY_TABLE
        )
        SESSION_SQLALCHEMY_SEQUENCE = config.get(
            "SESSION_SQLALCHEMY_SEQUENCE", Defaults.SESSION_SQLALCHEMY_SEQUENCE
        )
        SESSION_SQLALCHEMY_SCHEMA = config.get(
            "SESSION_SQLALCHEMY_SCHEMA", Defaults.SESSION_SQLALCHEMY_SCHEMA
        )
        SESSION_SQLALCHEMY_BIND_KEY = config.get(
            "SESSION_SQLALCHEMY_BIND_KEY", Defaults.SESSION_SQLALCHEMY_BIND_KEY
        )
        SESSION_CLEANUP_N_REQUESTS = config.get(
            "SESSION_CLEANUP_N_REQUESTS", Defaults.SESSION_CLEANUP_N_REQUESTS
        )

        # DynamoDB settings
        SESSION_DYNAMODB = config.get("SESSION_DYNAMODB", Defaults.SESSION_DYNAMODB)
        SESSION_DYNAMODB_TABLE = config.get(
            "SESSION_DYNAMODB_TABLE", Defaults.SESSION_DYNAMODB_TABLE
        )

        common_params = {
            "app": app,
            "key_prefix": SESSION_KEY_PREFIX,
            "use_signer": SESSION_USE_SIGNER,
            "permanent": SESSION_PERMANENT,
            "sid_length": SESSION_ID_LENGTH,
            "serialization_format": SESSION_SERIALIZATION_FORMAT,
        }

        SESSION_TYPE = SESSION_TYPE.lower()

        if SESSION_TYPE == "redis":
            from .redis import RedisSessionInterface

            session_interface = RedisSessionInterface(
                **common_params,
                client=SESSION_REDIS,
            )
        elif SESSION_TYPE == "memcached":
            from .memcached import MemcachedSessionInterface

            session_interface = MemcachedSessionInterface(
                **common_params,
                client=SESSION_MEMCACHED,
            )
        elif SESSION_TYPE == "filesystem":
            from .filesystem import FileSystemSessionInterface

            session_interface = FileSystemSessionInterface(
                **common_params,
                cache_dir=SESSION_FILE_DIR,
                threshold=SESSION_FILE_THRESHOLD,
                mode=SESSION_FILE_MODE,
            )
        elif SESSION_TYPE == "cachelib":
            from .cachelib import CacheLibSessionInterface

            session_interface = CacheLibSessionInterface(
                **common_params, client=SESSION_CACHELIB
            )
        elif SESSION_TYPE == "mongodb":
            from .mongodb import MongoDBSessionInterface

            session_interface = MongoDBSessionInterface(
                **common_params,
                client=SESSION_MONGODB,
                db=SESSION_MONGODB_DB,
                collection=SESSION_MONGODB_COLLECT,
            )
        elif SESSION_TYPE == "sqlalchemy":
            from .sqlalchemy import SqlAlchemySessionInterface

            session_interface = SqlAlchemySessionInterface(
                **common_params,
                client=SESSION_SQLALCHEMY,
                table=SESSION_SQLALCHEMY_TABLE,
                sequence=SESSION_SQLALCHEMY_SEQUENCE,
                schema=SESSION_SQLALCHEMY_SCHEMA,
                bind_key=SESSION_SQLALCHEMY_BIND_KEY,
                cleanup_n_requests=SESSION_CLEANUP_N_REQUESTS,
            )
        elif SESSION_TYPE == "dynamodb":
            from .dynamodb import DynamoDBSessionInterface

            session_interface = DynamoDBSessionInterface(
                **common_params,
                client=SESSION_DYNAMODB,
                table_name=SESSION_DYNAMODB_TABLE,
            )

        else:
            raise ValueError(f"Unrecognized value for SESSION_TYPE: {SESSION_TYPE}")

        return session_interface
