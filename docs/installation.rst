
Installation
============

Install from PyPI using an installer such as pip:

.. code-block:: bash

    $ pip install Flask-Session

Flask-Session's only required dependency is msgspec for serialization, which has no sub-dependencies.

However, you also need to choose a storage type and install an appropriate client library so the app can communicate with storage. 
For example, if you want to use Redis as your storage, you will need to install the redis-py_ library either directly or as an optional dependency like below:

.. code-block:: bash

    $ pip install Flask-Session[redis]

Redis is the recommended storage type for Flask-Session, as it has the most complete support for the features of Flask-Session with minimal configuration.

.. warning::

  Flask-Session versions below 1.0.0 (not yet released), use pickle_ as the default serializer, which may have security implications in production if your storage is ever compromised.


Available storage options
^^^^^^^^^^^^^^^^^^^^^^^^^

To install Flask-Session with support for a specific storage backend, use the following command, replacing ``<storage-option>`` with your chosen backend from the list below:

.. code-block:: bash

    pip install Flask-Session[<storage-option>]

Available storage options and their corresponding ``<storage-option>`` values are:


.. list-table::
   :header-rows: 1
   :align: left

   * - Storage
     - <storage-option>
     - Default client library
     - Alternative client libraries
   * - **Redis**
     - ``redis``
     - redis-py_
     -
   * - **Memcached**
     - ``memcached``
     - pymemcache_
     - pylibmc_, python-memcached_, libmc_ 
   * - **MongoDB**
     - ``mongodb``
     - pymongo_
     -
   * - **CacheLib**
     - ``cachelib``
     - cachelib_
     -
   * - **SQLAlchemy**
     - ``sqlalchemy``
     - flask-sqlalchemy_
     -
   * - **DynamoDB**
     - ``dynamodb``
     - boto3_
     -

Other storage backends might be compatible with Flask-Session as long as they adhere to the command interfaces used by the libraries listed above.

Cachelib
--------

Flask-Session also indirectly supports storage and client libraries via cachelib_, which is a wrapper around various cache libraries. 
You must also install cachelib_ itselfand the relevant client library to use these.

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
.. _flask-sqlalchemy: https://github.com/pallets-eco/flask-sqlalchemy
.. _cachelib: https://cachelib.readthedocs.io/en/stable/
.. _google.appengine.api.memcached: https://cloud.google.com/appengine/docs/legacy/standard/python/memcache
.. _boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
.. _libmc: https://github.com/douban/libmc
.. _uwsgi: https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html
.. _pickle: https://docs.python.org/3/library/pickle.html
