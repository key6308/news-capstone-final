Quickstart and usage
====================

This page assumes the application is running at http://127.0.0.1:8000/ (see
:doc:`installation`).

Load demo data
--------------

The quickest way to try every role is to load the demo data:

.. code-block:: powershell

   python manage.py seed_demo

This creates a publisher called *Demo News*, one approved article, an API
token for each user, and three accounts that share the password
``DemoPass123!``:

.. list-table::
   :header-rows: 1

   * - Username
     - Role
     - Notes
   * - ``demo_reader``
     - Reader
     - Subscribed to *Demo News* and to ``demo_writer``.
   * - ``demo_writer``
     - Journalist
     - Affiliated with *Demo News*.
   * - ``demo_editor``
     - Editor
     - Editor for *Demo News*.

.. warning::

   The demo accounts use a published password. Use them only on your own
   computer and never on a public server.

Walkthrough
-----------

1. **Sign in as the journalist.** Go to ``/login/`` and sign in as
   ``demo_writer``. Choose **Submit article**, enter a title and content, and
   optionally choose *Demo News* as the publisher. The article is saved
   *unapproved*, so it is not yet on the home page.
2. **Approve it as the editor.** Sign out, sign in as ``demo_editor``, and
   open **Review articles** (``/editor/review/``). Select **Approve**. The
   application emails the article to subscribed readers. In local
   development emails are printed to the terminal running ``runserver``.
3. **Read it as the reader.** Sign in as ``demo_reader``. The article is on
   the home page. Open **Subscriptions** (``/subscriptions/``) to change which
   publishers and journalists you follow.
4. **Create a newsletter.** As the journalist or editor, open **Newsletters**
   and choose **Create newsletter** to bundle approved articles together.

To create your own accounts, use **Register** (``/register/``) and pick the
reader or journalist role. Editor accounts are created by an administrator in
the Django admin site (``/admin/``).

Web pages
---------

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - URL
     - Who can use it
     - Purpose
   * - ``/``
     - Everyone
     - Approved articles.
   * - ``/register/``
     - Everyone
     - Create a reader or journalist account.
   * - ``/login/``, ``/logout/``
     - Everyone
     - Sign in and out.
   * - ``/articles/<id>/``
     - Signed-in users
     - Read an approved article.
   * - ``/articles/new/``
     - Journalists
     - Submit an article.
   * - ``/articles/<id>/edit/``, ``/articles/<id>/delete/``
     - Editors; journalists for their own independent articles
     - Change or remove an article.
   * - ``/editor/review/``
     - Editors
     - Articles waiting for approval.
   * - ``/newsletters/``
     - Signed-in users
     - Browse newsletters.
   * - ``/newsletters/new/``, ``/newsletters/<id>/edit/``,
       ``/newsletters/<id>/delete/``
     - Journalists and editors
     - Manage newsletters.
   * - ``/subscriptions/``
     - Readers
     - Follow publishers and journalists.
   * - ``/admin/``
     - Staff users
     - Django admin site.

Each page is implemented by a view in :mod:`news.views`.

Run the tests
-------------

.. code-block:: powershell

   python manage.py test

The tests need the database server to be reachable, because Django creates a
temporary test database.
