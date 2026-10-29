"""Serializers for converting application models to API representations.

Serializers define exposed fields and validate relationships submitted to the
REST API.
"""

from rest_framework import serializers

from news.models import ApprovedArticleLog, Article, Newsletter, Publisher, User


class UserSerializer(serializers.ModelSerializer):
    """Define the UserSerializer class."""
    class Meta:
        """Define the Meta class."""
        model = User
        fields = ('id', 'username', 'email', 'role')


class PublisherSerializer(serializers.ModelSerializer):
    """Define the PublisherSerializer class."""
    editors = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    journalists = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        """Define the Meta class."""
        model = Publisher
        fields = ('id', 'name', 'description', 'editors', 'journalists')


class ArticleSerializer(serializers.ModelSerializer):
    """Define the ArticleSerializer class."""
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    publisher = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(), allow_null=True, required=False
    )

    class Meta:
        """Define the Meta class."""
        model = Article
        fields = ('id', 'title', 'content', 'author', 'publisher', 'created_at', 'approved')
        read_only_fields = ('id', 'author', 'created_at', 'approved')

    def validate(self, attrs):
        """Validate validate data."""
        request = self.context['request']
        publisher = attrs.get('publisher')
        if request.method == 'POST':
            if publisher and not publisher.journalists.filter(pk=request.user.pk).exists():
                raise serializers.ValidationError(
                    'You must be affiliated with a publisher to submit publisher content.'
                )
        return attrs

    def create(self, validated_data):
        """Create for the application."""
        request = self.context['request']
        publisher = validated_data.get('publisher')
        article = Article(
            **validated_data,
            author=None if publisher else request.user,
            approved=False,
        )
        article.full_clean()
        article.save()
        return article


class NewsletterSerializer(serializers.ModelSerializer):
    """Define the NewsletterSerializer class."""
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    articles = serializers.PrimaryKeyRelatedField(many=True, read_only=False)

    class Meta:
        """Define the Meta class."""
        model = Newsletter
        fields = ('id', 'title', 'description', 'created_at', 'author', 'articles')
        read_only_fields = ('id', 'created_at', 'author')


class ApprovedArticleLogSerializer(serializers.ModelSerializer):
    """Define the ApprovedArticleLogSerializer class."""
    class Meta:
        """Define the Meta class."""
        model = ApprovedArticleLog
        fields = ('id', 'article', 'article_title', 'approved_at', 'source')
        read_only_fields = ('id', 'approved_at')
