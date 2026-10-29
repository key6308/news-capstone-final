Git workflow
============

The project uses a ``main`` branch for the integrated application, a ``docs``
branch for docstrings and Sphinx source, and a ``container`` branch for Docker
configuration. The assignment asks that the documentation changes and the
container changes be merged into ``main`` after their respective work is
committed.

Useful checks before submission::

   git branch -a
   git log --graph --oneline --decorate --all
   git status

Generated HTML documentation can be rebuilt from the repository root with
``python -m sphinx -b html docs docs/_build/html``. Commit the generated HTML
folder after a successful build so a reviewer can browse it from the repository.
