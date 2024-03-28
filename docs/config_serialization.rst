Serialization
------------------------------------

.. warning::

    Flask-session versions below 1.0.0 use pickle serialization (or fallback) for session storage. While not a direct vulnerability, it is a potential security risk. If you are using a version below 1.0.0, it is recommended to upgrade to the latest version as soon as it's available.

From 0.7.0 the serializer is msgspec. The format it uses is configurable with ``SESSION_SERIALIZATION_FORMAT``. The default format is ``'msgpack'`` which has 30% storage reduction compared to ``'json'``. The ``'json'`` format may be helpful for debugging, easier viewing or compatibility. Switching between the two should be seamless, even for existing sessions.

All sessions that are accessed or modified while using 0.7.0 will convert to a msgspec format. Once using 1.0.0, any sessions that are still in pickle format will be cleared upon access.

The msgspec library has speed and memory advantages over other libraries. However, if you want to use a different library (such as pickle or orjson), you can override the :attr:`session_interface.serializer`.

If you encounter a TypeError such as: "Encoding objects of type <type> is unsupported", you may be attempting to serialize an unsupported type. In this case, you can either convert the object to a supported type or use a different serializer.

Casting to a supported type:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    session["status"] = str(LazyString('done')))


.. note::

    Flask's flash method uses the session to store messages so you must also pass supported types to the flash method.


For a detailed list of supported types by the msgspec serializer, please refer to the official documentation at `msgspec supported types <https://jcristharif.com/msgspec/supported-types.html>`_.

Overriding the serializer:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from flask_session import Session
    import orjson

    app = Flask(__name__)
    Session(app)

    # Override the serializer
    app.session_interface.serializer = orjson

Any serializer that has a ``dumps`` and ``loads`` method can be used.