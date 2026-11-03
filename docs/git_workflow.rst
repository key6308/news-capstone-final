Git workflow
============

The repository uses three branches:

* ``main`` -- the integrated application.
* ``docs`` -- docstrings and Sphinx documentation.
* ``container`` -- Docker configuration.

Work on ``docs`` and ``container`` is merged into ``main`` once it is
committed.

Useful checks before submission:

.. code-block:: powershell

   git branch -a
   git log --graph --oneline --decorate --all
   git status

After rebuilding the documentation (see :doc:`building_docs`), commit the
``docs/_build/html/`` folder too, so reviewers can open the HTML directly from
the repository.
