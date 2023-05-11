API
---

.. module:: flask_session

.. autoclass:: Session
   :members: init_app

.. autoclass:: flask_session.sessions.ServerSideSession

   .. attribute:: sid

       Session id, internally we use :func:`uuid.uuid4` to generate one
       session id. You can access it with ``session.sid``.

.. autoclass:: NullSessionInterface
.. autoclass:: RedisSessionInterface
.. autoclass:: MemcachedSessionInterface
.. autoclass:: FileSystemSessionInterface
.. autoclass:: MongoDBSessionInterface
.. autoclass:: SqlAlchemySessionInterface
