"""Database models for the Django News Application.

The models define role-based users, publishers, articles, newsletters, and the
log entry created when an article is approved.
"""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Publisher(models.Model):
    """A publisher account that can own articles and have subscribers."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    editors = models.ManyToManyField(
        'User', related_name='edited_publishers', blank=True
    )
    journalists = models.ManyToManyField(
        'User', related_name='journalist_publishers', blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Define the Meta class."""
        ordering = ['name']

    def __str__(self):
        """Return a readable string representation."""
        return self.name


class User(AbstractUser):
    """Application user with a reader, editor, or journalist role."""
    class Roles(models.TextChoices):
        """Define the Roles class."""
        READER = 'reader', 'Reader'
        EDITOR = 'editor', 'Editor'
        JOURNALIST = 'journalist', 'Journalist'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.READER)
    subscribed_publishers = models.ManyToManyField(
        Publisher, related_name='subscriber_users', blank=True
    )
    subscribed_journalists = models.ManyToManyField(
        'self', related_name='journalist_subscribers', blank=True, symmetrical=False
    )

    def clean(self):
        """Validate clean data."""
        super().clean()
        if self.role == self.Roles.JOURNALIST:
            # Journalist accounts should not hold reader subscriptions.
            if self.pk and self.subscribed_publishers.exists():
                raise ValidationError('Journalists cannot have publisher subscriptions.')
            if self.pk and self.subscribed_journalists.exists():
                raise ValidationError('Journalists cannot have journalist subscriptions.')

    @property
    def is_reader(self):
        """Is reader for the application."""
        return self.role == self.Roles.READER

    @property
    def is_editor(self):
        """Is editor for the application."""
        return self.role == self.Roles.EDITOR

    @property
    def is_journalist(self):
        """Is journalist for the application."""
        return self.role == self.Roles.JOURNALIST

    def __str__(self):
        """Return a readable string representation."""
        return f'{self.username} ({self.get_role_display()})'


class Article(models.Model):
    """A news article owned by either a journalist or a publisher."""
    title = models.CharField(max_length=250)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='independent_articles',
        null=True,
        blank=True,
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='articles',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        """Define the Meta class."""
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=(
                    (Q(author__isnull=False) & Q(publisher__isnull=True))
                    | (Q(author__isnull=True) & Q(publisher__isnull=False))
                ),
                name='article_exactly_one_owner',
            )
        ]

    def clean(self):
        """Validate clean data."""
        super().clean()
        if bool(self.author_id) == bool(self.publisher_id):
            raise ValidationError(
                'An article must be associated with either a journalist or a publisher, not both.'
            )
        if self.author_id and self.author.role != User.Roles.JOURNALIST:
            raise ValidationError('Independent article authors must be journalists.')

    def __str__(self):
        """Return a readable string representation."""
        return self.title


class Newsletter(models.Model):
    """A curated collection of approved articles."""
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='newsletters'
    )
    articles = models.ManyToManyField(Article, related_name='newsletters', blank=True)

    class Meta:
        """Define the Meta class."""
        ordering = ['-created_at']

    def clean(self):
        """Validate clean data."""
        super().clean()
        if self.author_id and self.author.role not in {
            User.Roles.JOURNALIST,
            User.Roles.EDITOR,
        }:
            raise ValidationError('Only journalists and editors can create newsletters.')

    def __str__(self):
        """Return a readable string representation."""
        return self.title


class ApprovedArticleLog(models.Model):
    """Define the ApprovedArticleLog class."""
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    article_title = models.CharField(max_length=250)
    approved_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100, default='internal approval workflow')

    def __str__(self):
        """Return a readable string representation."""
        return f'Approved: {self.article_title}'
