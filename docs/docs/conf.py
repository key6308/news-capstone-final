"""Sphinx configuration for the Django News Application documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_application.settings")

import django

django.setup()

project = "Django News Application"
author = "Capstone Project"
release = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]
html_theme = "sphinx_rtd_theme"
html_title = "Django News Application Documentation"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
