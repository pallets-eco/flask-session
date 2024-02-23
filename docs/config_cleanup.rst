Scheduled session cleanup
-------------------------


.. important ::

    In the case of ``SQLAlchemy``, expired sessions are not automatically deleted from the database. You must use one of the following scheduled cleanup methods.


Run the the following command regularly with a cron job or scheduler such as Heroku Scheduler to clean up expired sessions. This is the recommended way to clean up expired sessions.

.. code-block:: bash

    flask session_cleanup

Alternatively, set the configuration variable ``SESSION_CLEANUP_N_REQUESTS`` to the average number of requests after which the cleanup should be performed. This is less desirable than using the scheduled app command cleanup as it may slow down some requests but may be useful for small applications or rapid development.

This is not required for the ``Redis``, ``Memecached``, ``Filesystem``, ``Mongodb`` storage engines, as they support time-to-live for records.