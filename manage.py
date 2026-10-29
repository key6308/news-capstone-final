"""Command-line entry point for Django management commands."""

#!/usr/bin/env python
import os
import sys


def main():
    """Main for the application."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_application.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            'Django is not installed. Run: pip install -r requirements.txt'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
