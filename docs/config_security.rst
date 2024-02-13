
Security configuration
----------------------

Please refer to documentation for `Flask`_, `OWASP`_, and other security resources such as `MDN`_ for more information.

.. _Flask: https://flask.palletsprojects.com/en/2.3.x/security/#set-cookie-options
.. _MDN: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
.. _OWASP: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

Consider the following Flask configurations in production:

.. list-table::
   :header-rows: 1

   * - Setting
     - Consideration
   * - SESSION_COOKIE_SECURE
     - Set to ``True`` if your application is served over HTTPS.
   * - SESSION_COOKIE_NAME
     - Use ``__Secure-`` or ``__Host-`` prefix according to MDN docs.
   * - SESSION_COOKIE_SAMESITE
     - Use ``Lax`` or ``Strict``

You can use a security plugin such as ``Flask-Talisman`` to set these and more.