Project overview
================

What the application does
-------------------------

* User registration as a reader or journalist (editors are created by an
  administrator).
* Article submission, editing, review, and approval.
* Independent articles (owned by a journalist) and publisher articles (owned
  by a publisher the journalist is affiliated with).
* Reader subscriptions to publishers and individual journalists.
* Newsletters that collect approved articles.
* Email notification of subscribers when an article is approved.
* A token-authenticated REST API built with Django REST Framework.
* Automated tests and this Sphinx documentation.

User roles
----------

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Role
     - What they can do
   * - Reader
     - Read approved articles and newsletters, and manage subscriptions to
       publishers and journalists.
   * - Journalist
     - Submit articles (independently or for an affiliated publisher), edit
       or delete their own independent articles, and create newsletters.
       Editing an article sends it back for approval.
   * - Editor
     - Review and approve submitted articles, edit or delete any article, and
       manage newsletters.

Each user is also placed in a Django permission group named after their role
(see :mod:`news.signals`).

How article approval works
--------------------------

1. A journalist submits an article. It is saved with ``approved = False``.
2. An editor opens **Review articles** and approves it.
3. :func:`news.services.approve_article_and_notify` marks the article as
   approved, emails every reader subscribed to the article's publisher or
   journalist, and calls the ``/api/approved/`` endpoint, which creates an
   :class:`~news.models.ApprovedArticleLog` entry.
4. The article now appears on the home page and in the API.

Technology
----------

* Python 3.12, Django 5.1, Django REST Framework 3.15
* MySQL or MariaDB (through the PyMySQL driver)
* Docker and Docker Compose for an all-in-one local environment
* Sphinx with the Read the Docs theme for this documentation

Project layout
--------------

.. code-block:: text

   manage.py                 Django command-line entry point
   news_application/         Project settings and top-level URL routes
   news/                     The news app
       models.py             Database models
       forms.py              HTML forms
       views.py              HTML page views
       services.py           Approval and notification logic
       signals.py            Role permission-group handlers
       api/                  REST API serializers, permissions, and views
       management/commands/  The seed_demo command
       templates/, static/   HTML templates and CSS
       tests.py              Automated tests
   Planning/                 Requirements, design, and test planning notes
   docs/                     Sphinx sources; built HTML is in docs/_build/html
   Dockerfile, compose.yaml  Container configuration
   requirements.txt          Pinned Python dependencies
