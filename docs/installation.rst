
Installation
============

Install from PyPI using an installer such as pip:

.. code-block:: bash

    $ pip install Flask-Session

Flask-Session's only required dependency is msgspec for serialization, which has no sub-dependencies. 

.. note::

  You need to choose a storage type and install an appropriate client library, unless you are using the FileSystemCache.

For example, if you want to use Redis as your storage, you will need to install the redis-py client library:

.. code-block:: bash

    $ pip install redis


Supported storage and client libraries:


.. list-table::
   :header-rows: 1

   * - Storage
     - Client Library
   * - Redis
     - redis-py_
   * - Memcached
     - pylibmc_, python-memcached_, pymemcache_
   * - MongoDB
     - pymongo_
   * - SQL Alchemy
     - flask-sqlalchemy_

Other clients may work if they use the same commands as the ones listed above.

.. _redis-py: https://github.com/andymccurdy/redis-py
.. _pylibmc: http://sendapatch.se/projects/pylibmc/
.. _python-memcached: https://github.com/linsomniac/python-memcached
.. _pymemcache: https://github.com/pinterest/pymemcache
.. _pymongo: http://api.mongodb.org/python/current/index.html
.. _Flask-SQLAlchemy: https://github.com/pallets-eco/flask-sqlalchemy