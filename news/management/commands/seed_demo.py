"""Application module for the Django news project."""
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from news.models import Article, Publisher, User


class Command(BaseCommand):
    """Define the Command class."""
    help = 'Create a small set of demo users, publisher, subscriptions, and articles.'

    def handle(self, *args, **options):
        """Run this management command."""
        reader, _ = User.objects.get_or_create(username='demo_reader', defaults={'role': User.Roles.READER, 'email': 'reader@example.com'})
        reader.role = User.Roles.READER
        reader.set_password('DemoPass123!')
        reader.save()

        editor, _ = User.objects.get_or_create(username='demo_editor', defaults={'role': User.Roles.EDITOR, 'email': 'editor@example.com'})
        editor.role = User.Roles.EDITOR
        editor.set_password('DemoPass123!')
        editor.save()

        journalist, _ = User.objects.get_or_create(username='demo_writer', defaults={'role': User.Roles.JOURNALIST, 'email': 'writer@example.com'})
        journalist.role = User.Roles.JOURNALIST
        journalist.set_password('DemoPass123!')
        journalist.save()

        publisher, _ = Publisher.objects.get_or_create(name='Demo News')
        publisher.editors.add(editor)
        publisher.journalists.add(journalist)
        reader.subscribed_publishers.add(publisher)
        reader.subscribed_journalists.add(journalist)

        Article.objects.get_or_create(
            title='Demo approved story',
            defaults={'content': 'This is sample approved content.', 'author': journalist, 'approved': True},
        )
        for user in (reader, editor, journalist):
            Token.objects.get_or_create(user=user)

        self.stdout.write(self.style.SUCCESS('Demo data created. Password for all demo users: DemoPass123!'))
