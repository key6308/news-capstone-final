REST API endpoints
==================

The REST API is served under ``/api/`` and is built with Django REST
Framework. Routes are defined in :mod:`news.api_urls`, and the views are
documented in :mod:`news.api.views`.

Authentication
--------------

Every endpoint except ``/api/token/`` needs an API token. Request one with a
username and password:

.. code-block:: powershell

   Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/token/ `
       -ContentType "application/json" `
       -Body '{"username": "demo_reader", "password": "DemoPass123!"}'

The response looks like ``{"token": "<your token>"}``. Send it on every other
request in the ``Authorization`` header:

.. code-block:: text

   Authorization: Token <your token>

For example, with ``curl``:

.. code-block:: bash

   curl -H "Authorization: Token <your token>" http://127.0.0.1:8000/api/articles/

.. warning::

   Treat tokens like passwords. Do not commit them or paste them in public.

Endpoints
---------

.. list-table::
   :header-rows: 1
   :widths: 12 30 20 38

   * - Method
     - Path
     - Allowed roles
     - Description
   * - POST
     - ``/api/token/``
     - Anyone
     - Exchange a username and password for a token.
   * - GET
     - ``/api/articles/``
     - Any signed-in user
     - List approved articles.
   * - POST
     - ``/api/articles/``
     - Journalist
     - Submit an article (``title``, ``content``, optional ``publisher``).
       It starts unapproved.
   * - GET
     - ``/api/articles/subscribed/``
     - Reader
     - Approved articles from the reader's subscriptions.
   * - GET
     - ``/api/articles/<id>/``
     - Any signed-in user
     - One approved article.
   * - PUT / PATCH
     - ``/api/articles/<id>/``
     - Editor, or the journalist who owns it
     - Update an article. A journalist's update sends it back for approval.
   * - DELETE
     - ``/api/articles/<id>/``
     - Editor, or the journalist who owns it
     - Delete an article.
   * - GET
     - ``/api/publishers/``
     - Any signed-in user
     - List publishers.
   * - GET
     - ``/api/newsletters/``
     - Any signed-in user
     - List newsletters that contain approved articles.
   * - POST
     - ``/api/newsletters/``
     - Editor, journalist
     - Create a newsletter (``title``, ``description``, ``articles``).
   * - GET
     - ``/api/users/``
     - Any signed-in user
     - List users (ID, username, role). The email address is included only
       in the requesting user's own record.
   * - POST
     - ``/api/approved/``
     - Editor
     - Internal: log an approved article (``{"article_id": <id>}``).

Requests without a valid token receive *401 Unauthorized*; requests from a
role that is not allowed receive *403 Forbidden*.

Example: submit an article
--------------------------

.. code-block:: bash

   curl -X POST http://127.0.0.1:8000/api/articles/ \
        -H "Authorization: Token <journalist token>" \
        -H "Content-Type: application/json" \
        -d '{"title": "API Story", "content": "Story submitted through the API."}'

Response (``201 Created``):

.. code-block:: json

   {
     "id": 2,
     "title": "API Story",
     "content": "Story submitted through the API.",
     "author": 3,
     "publisher": null,
     "created_at": "2026-01-01T12:00:00-06:00",
     "approved": false
   }

Postman collection
------------------

``postman_collection.json`` in the project root contains ready-made requests
for these endpoints. Import it into Postman, set the ``base_url`` and
``token`` collection variables, and send the requests.
