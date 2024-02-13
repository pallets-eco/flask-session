Backend configuration
---------------------


Redis
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_REDIS

   A ``redis.Redis`` instance.
   
   Default: Instance connected to ``127.0.0.1:6379``


Memcached
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_MEMCACHED

   A ``memcache.Client`` instance.
   
   Default: Instance connected to ``127.0.0.1:6379``


FileSystem
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_FILE_DIR

   The directory where session files are stored.
   
   Default: ``flask_session`` directory under current working directory.

.. py:data:: SESSION_FILE_THRESHOLD
    
   The maximum number of items the session stores before it starts deleting some.
   
   Default: ``500``

.. py:data:: SESSION_FILE_MODE
    
   The file mode wanted for the session files.
   
   Default: ``0600``


MongoDB
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_MONGODB

   A ``pymongo.MongoClient`` instance.
   
   Default: Instance connected to ``127.0.0.1:27017``

.. py:data:: SESSION_MONGODB_DB
    
   The MongoDB database you want to use.
   
   Default: ``'flask_session'``

.. py:data:: SESSION_MONGODB_COLLECT
    
   The MongoDB collection you want to use.
   
   Default: ``'sessions'``


SqlAlchemy
~~~~~~~~~~~~~~~~~~~~~~~

.. py:data:: SESSION_SQLALCHEMY

   A ``flask_sqlalchemy.SQLAlchemy`` instance whose database connection URI is configured using the ``SQLALCHEMY_DATABASE_URI`` parameter.
   
   Must be set in flask_sqlalchemy version 3.0 or higher.

.. py:data:: SESSION_SQLALCHEMY_TABLE
    
   The name of the SQL table you want to use.
   
   Default: ``'sessions'``

.. py:data:: SESSION_SQLALCHEMY_SEQUENCE
    
   The name of the sequence you want to use for the primary key.
   
   Default: ``None``

.. py:data:: SESSION_SQLALCHEMY_SCHEMA
    
   The name of the schema you want to use.
   
   Default: ``None``

.. py:data:: SESSION_SQLALCHEMY_BIND_KEY
    
   The name of the bind key you want to use.
   
   Default: ``None``

.. versionadded:: 0.6
    ``SESSION_SQLALCHEMY_BIND_KEY``, ``SESSION_SQLALCHEMY_SCHEMA``, ``SESSION_SQLALCHEMY_SEQUENCE``
