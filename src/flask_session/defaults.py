import os


class Defaults:
    # Flask-session specific settings
    SESSION_TYPE = "null"
    SESSION_KEY_PREFIX = "session:"
    SESSION_USE_SIGNER = False
    SESSION_PERMANENT = True
    SESSION_SID_LENGTH = 3

    # Redis settings
    SESSION_REDIS = None

    # Memcached settings
    SESSION_MEMCACHED = None

    # Filesystem settings
    SESSION_FILE_DIR = os.path.join(os.getcwd(), "flask_session")
    SESSION_FILE_THRESHOLD = 500
    SESSION_FILE_MODE = 384

    # MongoDB settings
    SESSION_MONGODB = None
    SESSION_MONGODB_DB = "flask_session"
    SESSION_MONGODB_COLLECT = "sessions"

    # SQLAlchemy settings
    SESSION_SQLALCHEMY = None
    SESSION_SQLALCHEMY_TABLE = "sessions"
    SESSION_SQLALCHEMY_SEQUENCE = None
    SESSION_SQLALCHEMY_SCHEMA = None
    SESSION_SQLALCHEMY_BIND_KEY = None
