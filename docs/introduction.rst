Introduction
=============

Flask-Session is an extension for `Flask`_ that adds support for server-side sessions to
your application.

.. _Flask: http://flask.palletsprojects.com/

In contrast to standard sessions, server-side sessions store session data in server-side storage 
rather than in a cookie on the client's browser. The cookie now only contains the session identifier 
that links the client to their corresponding data on the server.

.. image:: /_static/sequence.webp
   :alt: sequence diagram for flask-session
   :class: padded highlight