"""ASGI entry point that exposes the Django application as ``application``."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_application.settings')
application = get_asgi_application()
