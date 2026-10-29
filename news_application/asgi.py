"""Application module for the Django news project."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_application.settings')
application = get_asgi_application()
