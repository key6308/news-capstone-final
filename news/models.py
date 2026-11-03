"""Database models for the Django News Application.

The models define role-based users, publishers, articles, newsletters, and the
log entry created when an article is approved.
"""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Publisher(models.Model):
    """A news organisation that owns articles and can be followed by readers.

    Editors review articles submitted on behalf of the publisher, and
    journalists may submit articles under the publisher's name.

    Attributes:
        name (str): Unique display name of the publisher.
        description (str): Optional free-text description.
        editors (ManyToManyField): Editor users who review this publisher's
            articles.
        journalists (ManyToManyField): Journalist users affiliated with this
            publisher.
        created_at (datetime): When the publisher was created.
    """
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
        """Order publishers alphabetically by name."""
        ordering = ['name']

    def __str__(self):
        """Return the publisher name."""
        return self.name


class User(AbstractUser):
    """Application user with a reader, editor, or journalist role.

    Extends Django's :class:`~django.contrib.auth.models.AbstractUser`. The
    role decides which pages and API endpoints the user may access. Readers
    can subscribe to publishers and individual journalists.

    Attributes:
        role (str): One of the values in :class:`User.Roles`.
        subscribed_publishers (ManyToManyField): Publishers a reader follows.
        subscribed_journalists (ManyToManyField): Journalists a reader follows.
    """
    class Roles(models.TextChoices):
        """The account roles supported by the application."""
        READER = 'reader', 'Reader'
        EDITOR = 'editor', 'Editor'
        JOURNALIST = 'journalist', 'Journalist'

    role = models.CharField(
        max_length=20, choices=Roles.choices, default=Roles.READER
    )
    subscribed_publishers = models.ManyToManyField(
        Publisher, related_name='subscriber_users', blank=True
    )
    subscribed_journalists = models.ManyToManyField(
        'self',
        related_name='journalist_subscribers',
        blank=True,
        symmetrical=False,
    )

    @classmethod
    def from_db(cls, db, field_names, values):
        """Load a user and remember the role it was stored with.

        :mod:`news.signals` compares the remembered role with the current one
        so the permission group is only rebuilt when the role changes.
        """
        instance = super().from_db(db, field_names, values)
        if 'role' in field_names:
            instance._loaded_role = values[list(field_names).index('role')]
        return instance

    def clean(self):
        """Validate that journalists do not hold reader subscriptions.

        Raises:
            django.core.exceptions.ValidationError: If a saved journalist
                account has publisher or journalist subscriptions.
        """
        super().clean()
        if self.role == self.Roles.JOURNALIST:
            # Journalist accounts should not hold reader subscriptions.
            if self.pk and self.subscribed_publishers.exists():
                raise ValidationError(
                    'Journalists cannot have publisher subscriptions.'
                )
            if self.pk and self.subscribed_journalists.exists():
                raise ValidationError(
                    'Journalists cannot have journalist subscriptions.'
                )

    @property
    def is_reader(self):
        """bool: ``True`` if the user has the reader role."""
        return self.role == self.Roles.READER

    @property
    def is_editor(self):
        """bool: ``True`` if the user has the editor role."""
        return self.role == self.Roles.EDITOR

    @property
    def is_journalist(self):
        """bool: ``True`` if the user has the journalist role."""
        return self.role == self.Roles.JOURNALIST

    def can_modify(self, obj):
        """Return whether the user may edit or delete an article/newsletter.

        Editors may change any article or newsletter. Journalists may change
        only the ones they authored. Other roles may change nothing.

        Args:
            obj (Article | Newsletter): The object to change.

        Returns:
            bool: ``True`` if the change is allowed.
        """
        if self.is_editor:
            return True
        if self.is_journalist:
            return obj.author_id == self.pk
        return False

    def __str__(self):
        """Return the username and role, e.g. ``alice (Reader)``."""
        return f'{self.username} ({self.get_role_display()})'


class Article(models.Model):
    """A news article owned by either a journalist or a publisher.

    Exactly one of :attr:`author` and :attr:`publisher` must be set; a
    database check constraint enforces this. New and edited articles start
    unapproved until an editor approves them.

    Attributes:
        title (str): Headline of the article.
        content (str): Body text of the article.
        author (User): Journalist who owns an independent article, or ``None``.
        publisher (Publisher): Publisher that owns the article, or ``None``.
        created_at (datetime): When the article was created.
        approved (bool): Whether an editor has approved the article.
    """
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
        """Show newest articles first and require exactly one owner."""
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
        """Validate article ownership.

        Raises:
            django.core.exceptions.ValidationError: If the article has both or
                neither of an author and a publisher, or if the author is not
                a journalist.
        """
        super().clean()
        if bool(self.author_id) == bool(self.publisher_id):
            raise ValidationError(
                'An article must be associated with either a journalist or a '
                'publisher, not both.'
            )
        if self.author_id and self.author.role != User.Roles.JOURNALIST:
            raise ValidationError(
                'Independent article authors must be journalists.'
            )

    def __str__(self):
        """Return the article title."""
        return self.title


class Newsletter(models.Model):
    """A curated collection of approved articles.

    Attributes:
        title (str): Newsletter title.
        description (str): Optional summary shown with the newsletter.
        created_at (datetime): When the newsletter was created.
        author (User): Journalist or editor who created the newsletter.
        articles (ManyToManyField): Articles included in the newsletter.
    """
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='newsletters'
    )
    articles = models.ManyToManyField(
        Article, related_name='newsletters', blank=True
    )

    class Meta:
        """Show newest newsletters first."""
        ordering = ['-created_at']

    def clean(self):
        """Validate that the author is a journalist or an editor.

        Raises:
            django.core.exceptions.ValidationError: If a reader is set as the
                newsletter author.
        """
        super().clean()
        if self.author_id and self.author.role not in {
            User.Roles.JOURNALIST,
            User.Roles.EDITOR,
        }:
            raise ValidationError(
                'Only journalists and editors can create newsletters.'
            )

    def __str__(self):
        """Return the newsletter title."""
        return self.title


class ApprovedArticleLog(models.Model):
    """A record created through the API each time an article is approved.

    Attributes:
        article (Article): The approved article (one log entry per article).
        article_title (str): Title of the article when it was approved.
        approved_at (datetime): When the log entry was created.
        source (str): Short description of what triggered the log entry.
    """
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    article_title = models.CharField(max_length=250)
    approved_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(
        max_length=100, default='internal approval workflow'
    )

    def __str__(self):
        """Return ``Approved: <article title>``."""
        return f'Approved: {self.article_title}'
