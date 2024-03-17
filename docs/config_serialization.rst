Serialization
------------------------------------

.. warning::

    Flask-session versions below 1.0.0 use pickle serialization (or fallback) for session storage. While not a direct vulnerability, it is a potential security risk. If you are using a version below 1.0.0, it is recommended to upgrade to the latest version as soon as it's available.

From 0.7.0 the serializer is msgspec, which is configurable using ``SESSION_SERIALIZATION_FORMAT``. The default format is ``'msgpack'`` which has 30% storage reduction compared to ``'json'``. The ``'json'`` format may be helpful for debugging, easier viewing or compatibility. Switching between the two should be seamless, even for existing sessions.

The msgspec library has speed and memory advantages over other libraries. However, if you want to use a different library (such as pickle or orjson), you can override the :attr:`session_interface.serializer`.
