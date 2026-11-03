"""The ``seed_demo`` management command, which creates local demo data.

Run it with ``python manage.py seed_demo``. The demo accounts share a known
password and must only be used for local testing.
"""
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from news.models import Article, Publisher, User

#: Password shared by every demo account. For local testing only.
DEMO_PASSWORD = 'DemoPass123!'


def get_or_create_demo_user(username, role, email):
    """Create or reset a demo user with the given role and the demo password.

    Args:
        username (str): The demo account's username.
        role (str): A value from :class:`news.models.User.Roles`.
        email (str): Email address used when the account is first created.

    Returns:
        news.models.User: The saved demo user.
    """
    user, _ = User.objects.get_or_create(
        username=username, defaults={'role': role, 'email': email}
    )
    user.role = role
    user.set_password(DEMO_PASSWORD)
    user.save()
    return user


class Command(BaseCommand):
    """Create demo reader, editor, and journalist accounts and sample content.

    The command is safe to run more than once: existing demo records are
    reused rather than duplicated.
    """
    help = (
        'Create a small set of demo users, publisher, subscriptions, and '
        'articles.'
    )

    def handle(self, *args, **options):
        """Create or update the demo users, publisher, article, and tokens."""
        reader = get_or_create_demo_user(
            'demo_reader', User.Roles.READER, 'reader@example.com'
        )
        editor = get_or_create_demo_user(
            'demo_editor', User.Roles.EDITOR, 'editor@example.com'
        )
        journalist = get_or_create_demo_user(
            'demo_writer', User.Roles.JOURNALIST, 'writer@example.com'
        )

        publisher, _ = Publisher.objects.get_or_create(name='Demo News')
        publisher.editors.add(editor)
        publisher.journalists.add(journalist)
        reader.subscribed_publishers.add(publisher)
        reader.subscribed_journalists.add(journalist)

        Article.objects.get_or_create(
            title='Demo approved story',
            defaults={
                'content': 'This is sample approved content.',
                'author': journalist,
                'approved': True,
            },
        )
        for user in (reader, editor, journalist):
            Token.objects.get_or_create(user=user)

        self.stdout.write(self.style.SUCCESS(
            f'Demo data created. Password for all demo users: {DEMO_PASSWORD}'
        ))
