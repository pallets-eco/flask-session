
Installation
============

Install from PyPI using an installer such as pip:

.. code-block:: bash

    $ pip install Flask-Session

Flask-Session has no dependencies other than those included with Flask. However, unless you are using the FileSystemCache, you need to choose and a backend and install an appropriate client library.

For example, if you want to use Redis as your backend, you will need to install the redis-py client library:

.. code-block:: bash

    $ pip install redis


Supported backends and client libraries:


.. list-table::
   :header-rows: 1

   * - Backend
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