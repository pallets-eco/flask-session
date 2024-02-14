Introduction
=============

Flask-Session is an extension for `Flask`_ that adds support for server-side sessions to
your application.

.. _Flask: http://flask.palletsprojects.com/

Client-side vs Server-side sessions
------------------------------------

Client-side sessions store session data in the client's browser. 
This is done by placing it in a cookie that is sent to and from the client on each request and response. 
This can be any small, basic information about that client or their interactions for quick retrieval (up to 4kB). 

Server-side sessions differ by storing session data in server-side storage. 
A cookie is also used but it only contains the session identifier that links the client to their corresponding data on the server.

.. note::
   There are no individual session size limitations on server-side sessions, 
   but developers should be cautious about abusing them for data which would be more suited for actual database storage.

Flask-Session sequence diagram
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /_static/sequence.webp
   :alt: sequence diagram for flask-session
   :class: padded highlight