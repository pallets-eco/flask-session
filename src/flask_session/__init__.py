from .defaults import Defaults
from .sessions import (
    FileSystemSessionInterface,
    MemcachedSessionInterface,
    MongoDBSessionInterface,
    NullSessionInterface,
    RedisSessionInterface,
    SqlAlchemySessionInterface,
)

__version__ = "0.6.0rc1"


class Session:
    """This class is used to add Server-side Session to one or more Flask
    applications.

    There are two usage modes.  One is initialize the instance with a very
    specific Flask application::

        app = Flask(__name__)
        Session(app)

    The second possibility is to create the object once and configure the
    application later::

        sess = Session()

        def create_app():
            app = Flask(__name__)
            sess.init_app(app)
            return app

    By default Flask-Session will use :class:`NullSessionInterface`, you
    really should configurate your app to use a different SessionInterface.

    .. note::

        You can not use ``Session`` instance directly, what ``Session`` does
        is just change the :attr:`~flask.Flask.session_interface` attribute on
        your Flask applications.
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """This is used to set up session for your app object.

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
        )
        SESSION_KEY_PREFIX = config.get(
            "SESSION_KEY_PREFIX", Defaults.SESSION_KEY_PREFIX
        )
        SESSION_SID_LENGTH = config.get(
            "SESSION_ID_LENGTH", Defaults.SESSION_SID_LENGTH
        )

        # Redis settings
        SESSION_REDIS = config.get("SESSION_REDIS", Defaults.SESSION_REDIS)

        # Memcached settings
        SESSION_MEMCACHED = config.get("SESSION_MEMCACHED", Defaults.SESSION_MEMCACHED)

        # Filesystem settings
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

        common_params = {
            "key_prefix": SESSION_KEY_PREFIX,
            "use_signer": SESSION_USE_SIGNER,
            "permanent": SESSION_PERMANENT,
            "sid_length": SESSION_SID_LENGTH,
        }

        if SESSION_TYPE == "redis":
            session_interface = RedisSessionInterface(
                **common_params,
                redis=SESSION_REDIS,
            )
        elif SESSION_TYPE == "memcached":
            session_interface = MemcachedSessionInterface(
                **common_params,
                client=SESSION_MEMCACHED,
            )
        elif SESSION_TYPE == "filesystem":
            session_interface = FileSystemSessionInterface(
                **common_params,
                cache_dir=SESSION_FILE_DIR,
                threshold=SESSION_FILE_THRESHOLD,
                mode=SESSION_FILE_MODE,
            )
        elif SESSION_TYPE == "mongodb":
            session_interface = MongoDBSessionInterface(
                **common_params,
                client=SESSION_MONGODB,
                db=SESSION_MONGODB_DB,
                collection=SESSION_MONGODB_COLLECT,
            )
        elif SESSION_TYPE == "sqlalchemy":
            session_interface = SqlAlchemySessionInterface(
                **common_params,
                app=app,
                db=SESSION_SQLALCHEMY,
                table=SESSION_SQLALCHEMY_TABLE,
                sequence=SESSION_SQLALCHEMY_SEQUENCE,
                schema=SESSION_SQLALCHEMY_SCHEMA,
                bind_key=SESSION_SQLALCHEMY_BIND_KEY,
            )
        else:
            session_interface = NullSessionInterface()

        return session_interface
