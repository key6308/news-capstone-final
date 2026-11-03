Django News Application
=======================

The Django News Application is a newsroom website with three kinds of
accounts. **Journalists** write articles, **editors** review and approve them,
and **readers** browse approved stories and subscribe to the publishers and
journalists they like. Approved articles are emailed to subscribers, and a
token-authenticated REST API exposes the same content to other programs.

.. note::

   This HTML documentation is pre-built and stored in the repository at
   ``docs/_build/html/``. Open ``docs/_build/html/index.html`` in a web
   browser to read it. You do not need to install anything to view it.

Where to start
--------------

* New to the project? Read the :doc:`overview` first.
* Want to run it? Follow :doc:`installation`, then :doc:`quickstart`.
* Calling the HTTP API? See :doc:`rest_api`.
* Looking for a class or function? Browse the :doc:`api/index`.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   overview
   installation
   quickstart
   rest_api
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Developer reference

   api/index
   building_docs
   git_workflow

Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
