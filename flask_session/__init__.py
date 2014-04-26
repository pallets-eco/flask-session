# -*- coding: utf-8 -*-
"""
    flaskext.session
    ~~~~~~~~~~~~~~~~

    Adds server session support to your application.

    :copyright: (c) 2014 by Shipeng Feng.
    :license: BSD, see LICENSE for more details.
"""
from .sessions import RedisSessionInterface


class Session(object):
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.session_interface = self.get_interface(app)

    def get_interface(self, app):
        config = app.config.copy()
        config.setdefault('SESSION_TYPE', 'redis')
        config.setdefault('SESSION_REDIS', None)
        config.setdefault('SESSION_PREFIX', 'session:')

        if config['SESSION_TYPE'] == 'redis':
            session_interface = RedisSessionInterface(config['SESSION_PREFIX'],
                                                      config['SESSION_REDIS'])
        else:
            session_interface = 'default'
        
        return session_interface
