"""WSGI entry point that exposes the Django application as ``application``."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_application.settings')
application = get_wsgi_application()
