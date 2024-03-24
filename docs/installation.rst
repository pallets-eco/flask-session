
Installation
============

Install from PyPI using an installer such as pip:

.. code-block:: bash

    $ pip install Flask-Session

Flask-Session's only required dependency is msgspec for serialization, which has no sub-dependencies. 

However, you also need to choose a storage type and install an appropriate client library so the app can communicate with storage. For example, if you want to use Redis as your storage, you will need to install the redis-py client library:

.. code-block:: bash

    $ pip install redis

Redis is the recommended storage type for Flask-Session, as it has the most complete support for the features of Flask-Session with minimal configuration.

.. warning::

  Flask-Session versions below 1.0.0 (not yet released), use pickle_ as the default serializer, which may have security implications in production if your storage is ever compromised.


Direct support
---------------

Flask-Session has an increasing number of directly supported storage and client libraries.

.. list-table::
   :header-rows: 1
   :align: left

   * - Storage
     - Client Library
   * - Redis
     - redis-py_
   * - Memcached
     - pylibmc_, python-memcached_, libmc_ or pymemcache_
   * - MongoDB
     - pymongo_
   * - SQL Alchemy
     - flask-sqlalchemy_

Other libraries may work if they use the same commands as the ones listed above.

Cachelib
--------

Flask-Session also indirectly supports storage and client libraries via cachelib_, which is a wrapper around various cache libraries. You must also install cachelib_ itself to use these.

.. list-table::
   :header-rows: 1
   :align: left

   * - Storage
     - Client Library
   * - File System
     - Not required
   * - Simple Memory
     - Not required
   * - UWSGI
     - uwsgi_
   * - Redis
     - redis-py_
   * - Memcached
     - pylibmc_, python-memcached_, libmc_ or `google.appengine.api.memcached`_
   * - MongoDB
     - pymongo_
   * - DynamoDB
     - boto3_
  

.. warning::

  As of writing, cachelib_ still uses pickle_ as the default serializer, which may have security implications in production if your storage is ever compromised.


.. _redis-py: https://github.com/redis/redis-py
.. _pylibmc: http://sendapatch.se/projects/pylibmc/
.. _python-memcached: https://github.com/linsomniac/python-memcached
.. _pymemcache: https://github.com/pinterest/pymemcache
.. _pymongo: https://pymongo.readthedocs.io/en/stable
.. _Flask-SQLAlchemy: https://github.com/pallets-eco/flask-sqlalchemy
.. _cachelib: https://cachelib.readthedocs.io/en/stable/
.. _google.appengine.api.memcached: https://cloud.google.com/appengine/docs/legacy/standard/python/memcache
.. _boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
.. _libmc: https://github.com/douban/libmc
.. _uwsgi: https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html
.. _pickle: https://docs.python.org/3/library/pickle.html