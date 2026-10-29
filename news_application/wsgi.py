"""Application module for the Django news project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_application.settings')
application = get_wsgi_application()
