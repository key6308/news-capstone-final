Project overview
================

User roles
----------

* **Reader:** reads approved content and manages subscriptions.
* **Journalist:** submits articles and may be affiliated with a publisher.
* **Editor:** reviews and approves submitted articles.

Main features
-------------

* User registration and role-based workflows.
* Article submission, editing, review, and approval.
* Publisher and journalist subscriptions.
* Newsletter pages.
* Email notifications for approved articles.
* Token-authenticated REST API endpoints.
* Django tests and Sphinx documentation.

Important configuration
-----------------------

The app reads database settings from environment variables. See
:doc:`setup` and the root ``.env.example`` file. Do not publish real passwords,
API tokens, or production secret keys.
