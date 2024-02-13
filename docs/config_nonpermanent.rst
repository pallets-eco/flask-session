Non-permanent session configuration
------------------------------------

.. warning::

    Flask-session is designed to be used with permanent sessions. If you want to use non-permanent sessions, you must set ``SESSION_PERMANENT`` and be aware of significant limitations.

Terminology:

- **Permanent session**: A session cookie is stored in the browser and not deleted until it expires (has expiry).
- **Non-permanent session**: A session cookie is stored in the browser and is deleted when the browser or tab is closed (no expiry).

Either cookie can be removed earlier if requested by the server, for example during logout.

In the case of a non-permanent, the server has no way to know when the browser is closed and the session cookie is deleted, so it cannot confidently know when to delete the stored session data. This can lead to a large number of stale sessions being stored on the server.

To mitigate this somewhat, Flask-Session always sets server-side expiration time using ``PERMANENT_SESSION_LIFETIME``. In addition, ``PERMANENT_SESSION_LIFETIME`` can be set to a very short time.

