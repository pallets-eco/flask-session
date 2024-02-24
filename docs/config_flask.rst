
Relevant Flask configuration values
-------------------------------------
The following configuration values are from 
Flask itself that are relate to the Flask session cookie set on the browser. Flask-Session
loads these values from your Flask application config, so you should configure
your app first before you pass it to Flask-Session.  

These values cannot be modified after the ``init_app`` was applied so make sure to not
modify them at runtime.

`SESSION_COOKIE_NAME`_

`SESSION_COOKIE_DOMAIN`_

`SESSION_COOKIE_PATH`_

`SESSION_COOKIE_HTTPONLY`_

`SESSION_COOKIE_SECURE`_

`SESSION_COOKIE_SAMESITE`_

`SESSION_REFRESH_EACH_REQUEST`_

`PERMANENT_SESSION_LIFETIME`_

.. _SESSION_COOKIE_NAME: https://flask.palletsprojects.com/en/latest/config/#SESSION_COOKIE_NAME
.. _SESSION_COOKIE_DOMAIN: https://flask.palletsprojects.com/en/latest/config/#SESSION_COOKIE_DOMAIN
.. _SESSION_COOKIE_PATH: https://flask.palletsprojects.com/en/latest/config/#SESSION_COOKIE_PATH
.. _SESSION_COOKIE_HTTPONLY: https://flask.palletsprojects.com/en/latest/config/#SESSION_COOKIE_HTTPONLY
.. _SESSION_COOKIE_SECURE: https://flask.palletsprojects.com/en/latest/config/#SESSION_COOKIE_SECURE
.. _SESSION_COOKIE_SAMESITE: https://flask.palletsprojects.com/en/latest/config/#SESSION_COOKIE_SAMESITE
.. _PERMANENT_SESSION_LIFETIME: https://flask.palletsprojects.com/en/latest/config/#PERMANENT_SESSION_LIFETIME
.. _SESSION_REFRESH_EACH_REQUEST: https://flask.palletsprojects.com/en/latest/config/#SESSION_REFRESH_EACH_REQUEST

.. note::
      ``PERMANENT_SESSION_LIFETIME`` is also used to set the expiration time of the session data on the server side, regardless of ``SESSION_PERMANENT``.
