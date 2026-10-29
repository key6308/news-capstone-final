User guide
==========

Web application
---------------

1. Start the application using the steps in :doc:`setup`.
2. Open ``http://127.0.0.1:8000/``.
3. Register an account and select the appropriate role.
4. Use the pages available to that role. Journalists can submit articles;
   editors can review articles; readers can browse approved content and manage
   subscriptions.

Demo content
------------

To create sample users and content, run::

   python manage.py seed_demo

This command creates demo accounts with a shared sample password. Use these
accounts only for local testing and never deploy them to a public service.

API token
---------

Request a token from ``/api/token/`` and send it on API requests using the
header ``Authorization: Token YOUR_TOKEN``. Replace ``YOUR_TOKEN`` with your
own token. Never paste a real token into a public repository.
