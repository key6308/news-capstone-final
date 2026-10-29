"""Application module for the Django news project."""
from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Define the NewsConfig class."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        """Ready for the application."""
        from . import signals  # noqa: F401
