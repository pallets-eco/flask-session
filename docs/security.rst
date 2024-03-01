Security
==========

.. warning::

  Flask is a micro-framework and does not provide all security features out of the box. It is important to configure security settings for your application.
  
Flask configuration
--------------------

Please refer to documentation for `Flask`_, `OWASP`_, and other resources such as `MDN`_ for the latest information on best practice.

Consider the following Flask configurations in production:

.. list-table::
   :header-rows: 1
   :align: left

   * - Setting
     - Consideration
   * - SESSION_COOKIE_SECURE
     - Set to ``True`` if your application is served over HTTPS.
   * - SESSION_COOKIE_NAME
     - Use ``__Secure-`` or ``__Host-`` prefix according to MDN docs.
   * - SESSION_COOKIE_SAMESITE
     - Use ``Lax`` or ``Strict``

You can use a security plugin such as `Flask-Talisman`_ to set these and more.

Storage
------------------

Take care to secure your storage and storage client connection. For example, setup SSL/TLS and storage authentication.
  

Session fixation
------------------

Session fixation is an attack that permits an attacker to hijack a valid user session. The attacker can fixate a user's session by providing them with a session identifier. The attacker can then use the session identifier to impersonate the user.

As one tool among others that can mitigate session fixation, is regenerating the session identifier when a user logs in. This can be done by calling the ``session.regenerate()`` method.

.. code-block:: python

    @app.route('/login')
    def login():
        # your login logic ...
        app.session_interface.regenerate(session)
        # your response ...

.. _Flask: https://flask.palletsprojects.com/en/2.3.x/security/#set-cookie-options
.. _MDN: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
.. _OWASP: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
.. _Flask-Talisman: https://github.com/wntrblm/flask-talisman