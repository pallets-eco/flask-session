__version__ = '0.1.0'

import os
import flask

from .sessions import FileSystemSessionInterface, MongoDBSessionInterface


class ServerSession(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: flask.Flask):
        config = app.config.copy()
        config.setdefault('SESSION_TYPE', 'null')

        config.setdefault('SESSION_PERMANENT', True)
        config.setdefault('SESSION_USE_SIGNER', False)
        config.setdefault('SESSION_KEY_PREFIX', 'session:')
        config.setdefault('SESSION_COOKIE_NAME', 'session')

        config.setdefault('SESSION_FILE_DIR', os.path.join(os.getcwd(), 'flask_session'))
        config.setdefault('SESSION_FILE_THRESHOLD', 500)
        config.setdefault('SESSION_FILE_MODE', 384)

        config.setdefault('SESSION_MONGODB', None)
        config.setdefault('SESSION_MONGODB_DB', 'flask_session')
        config.setdefault('SESSION_MONGODB_COLLECTION', 'sessions')

        if config['SESSION_TYPE'] == 'filesystem':
            app.config["SESSION_INTERFACE"] = FileSystemSessionInterface(
                config['SESSION_FILE_DIR'], config['SESSION_FILE_THRESHOLD'],
                config['SESSION_FILE_MODE'], config['SESSION_KEY_PREFIX'],
                config['SESSION_COOKIE_NAME'], config['SESSION_PERMANENT'])
        
        elif config['SESSION_TYPE'] == 'mongodb':
            if config['SESSION_MONGODB'] is None:
                raise ValueError('Missing MongoDB client, did you forget to set SESSION_MONGODB?')
            
            app.config["SESSION_INTERFACE"] = MongoDBSessionInterface(
                config['SESSION_MONGODB'], config['SESSION_MONGODB_DB'],
                config['SESSION_MONGODB_COLLECTION'], config['SESSION_KEY_PREFIX'],
                config['SESSION_COOKIE_NAME'], config['SESSION_PERMANENT'])
        
        else:
            raise ValueError('Not a valid session type')