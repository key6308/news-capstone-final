"""Django application configuration for the ``news`` app."""
from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration for the ``news`` app; registers its signal handlers."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        """Import :mod:`news.signals` so its receivers are connected."""
        from . import signals  # noqa: F401
