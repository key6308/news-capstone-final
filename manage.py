#!/usr/bin/env python
"""Command-line entry point for Django management commands.

Use this script for database migrations, system checks, tests, and the local
development server. Run commands from the repository root.
"""
import os
import sys


def main():
    """Point Django at the project settings and run the given command."""
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE', 'news_application.settings'
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            'Django is not installed. Run: pip install -r requirements.txt'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
