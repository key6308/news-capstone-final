"""Serializers for converting application models to API representations.

Serializers define exposed fields and validate relationships submitted to the
REST API.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from news.models import (
    ApprovedArticleLog,
    Article,
    Newsletter,
    Publisher,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    """Expose a user's ID, username, and role.

    The email address is only included when a user views their own record,
    so signed-in users cannot collect other users' addresses.
    """
    class Meta:
        """Serialize :class:`news.models.User`."""
        model = User
        fields = ('id', 'username', 'email', 'role')

    def to_representation(self, instance):
        """Return the user's data, without ``email`` unless it is their own.

        Args:
            instance (news.models.User): The user being serialized.

        Returns:
            dict: The serialized user.
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request is None or request.user.pk != instance.pk:
            data.pop('email', None)
        return data


class PublisherSerializer(serializers.ModelSerializer):
    """Expose a publisher with the IDs of its editors and journalists."""
    editors = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    journalists = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )

    class Meta:
        """Serialize :class:`news.models.Publisher`."""
        model = Publisher
        fields = ('id', 'name', 'description', 'editors', 'journalists')


class ArticleSerializer(serializers.ModelSerializer):
    """Read and write articles.

    The author and approval status are read-only: the author is set from the
    requesting journalist, and new articles always start unapproved.
    """
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    publisher = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(), allow_null=True, required=False
    )

    class Meta:
        """Serialize :class:`news.models.Article`."""
        model = Article
        fields = (
            'id', 'title', 'content', 'author', 'publisher', 'created_at',
            'approved',
        )
        read_only_fields = ('id', 'author', 'created_at', 'approved')

    def validate(self, attrs):
        """Check that a journalist choosing a publisher is affiliated with it.

        The check runs when a journalist creates (``POST``) or updates
        (``PUT``/``PATCH``) an article.

        Raises:
            rest_framework.serializers.ValidationError: If the requesting
                journalist is not one of the publisher's journalists.
        """
        user = self.context['request'].user
        publisher = attrs.get('publisher')
        if publisher and user.is_journalist:
            if not publisher.journalists.filter(pk=user.pk).exists():
                raise serializers.ValidationError(
                    'You must be affiliated with a publisher to submit '
                    'publisher content.'
                )
        return attrs

    @staticmethod
    def _validate_and_save(article):
        """Run model validation, then save the article.

        Raises:
            rest_framework.serializers.ValidationError: If
                :meth:`news.models.Article.clean` or field validation fails,
                so the client receives *400 Bad Request* instead of a
                database error.
        """
        try:
            article.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                serializers.as_serializer_error(exc)
            )
        article.save()
        return article

    def create(self, validated_data):
        """Create an unapproved article owned by the journalist or publisher.

        Returns:
            news.models.Article: The saved article.
        """
        request = self.context['request']
        publisher = validated_data.get('publisher')
        article = Article(
            **validated_data,
            author=None if publisher else request.user,
            approved=False,
        )
        return self._validate_and_save(article)

    def update(self, instance, validated_data):
        """Update an article and keep exactly one owner.

        As in :meth:`create`, an article with a publisher has no author. When
        a journalist removes the publisher, they become the author.

        Returns:
            news.models.Article: The saved article.
        """
        request = self.context['request']
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if instance.publisher_id:
            instance.author = None
        elif request.user.is_journalist:
            instance.author = request.user
        return self._validate_and_save(instance)


class NewsletterSerializer(serializers.ModelSerializer):
    """Read and write newsletters; the author is the requesting user."""
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    # A writable related field needs a queryset; like NewsletterForm, only
    # approved articles may be added to a newsletter.
    articles = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Article.objects.filter(approved=True)
    )

    class Meta:
        """Serialize :class:`news.models.Newsletter`."""
        model = Newsletter
        fields = (
            'id', 'title', 'description', 'created_at', 'author', 'articles',
        )
        read_only_fields = ('id', 'created_at', 'author')


class ApprovedArticleLogSerializer(serializers.ModelSerializer):
    """Expose an approval log entry."""
    class Meta:
        """Serialize :class:`news.models.ApprovedArticleLog`."""
        model = ApprovedArticleLog
        fields = ('id', 'article', 'article_title', 'approved_at', 'source')
        read_only_fields = ('id', 'approved_at')
