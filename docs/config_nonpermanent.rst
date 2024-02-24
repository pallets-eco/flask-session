Non-permanent sessions
------------------------------------

.. caution::

    Flask-session is primarily designed to be used with permanent sessions. If you want to use non-permanent sessions, you must set ``SESSION_PERMANENT=False`` and be aware of significant limitations.

Flask terminology regarding it's built-in client-side session is inherited by Flask-Session:

- **Permanent session**: A cookie is stored in the browser and not deleted until it expires (has expiry). Also known as a persistent cookie.
- **Non-permanent session**: A cookie is stored in the browser and is deleted when the browser or tab is closed (no expiry). Also known as a session cookie or non-persistent cookie.

Either cookie can be removed earlier if requested by the server, for example during logout.

In the case of non-permanent server-side sessions, the server has no way to know when the browser is closed and it's session cookie removed as a result, so it cannot confidently know when to delete the stored session data linked to that browser. This can lead to a large number of stale sessions being stored on the server.

To mitigate this somewhat, Flask-Session always sets server-side expiration time using ``PERMANENT_SESSION_LIFETIME``. As such, ``PERMANENT_SESSION_LIFETIME`` can be set to a very short time to further mitigate this.

