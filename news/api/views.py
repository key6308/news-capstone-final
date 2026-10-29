"""REST API endpoints for news content and subscriptions.

Endpoints apply authentication and role-based permissions before returning or
changing application data.
"""

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from news.models import ApprovedArticleLog, Article, Newsletter, Publisher, User

from .permissions import IsEditor, IsEditorOrJournalist, IsJournalist, IsReader
from .serializers import (
    ApprovedArticleLogSerializer,
    ArticleSerializer,
    NewsletterSerializer,
    PublisherSerializer,
    UserSerializer,
)


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """Define the ArticleListCreateAPIView class."""
    authentication_classes = [TokenAuthentication]
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """Return permissions appropriate for this request."""
        if self.request.method == 'POST':
            return [IsJournalist()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Return the records available to this request."""
        return Article.objects.filter(approved=True).select_related('author', 'publisher')


class SubscribedArticleListAPIView(generics.ListAPIView):
    """Define the SubscribedArticleListAPIView class."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsReader]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """Return the records available to this request."""
        user = self.request.user
        return Article.objects.filter(approved=True).filter(
            Q(publisher__in=user.subscribed_publishers.all())
            | Q(author__in=user.subscribed_journalists.all())
        ).distinct().select_related('author', 'publisher')


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Define the ArticleDetailAPIView class."""
    authentication_classes = [TokenAuthentication]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """Return the records available to this request."""
        queryset = Article.objects.select_related('author', 'publisher').all()
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            queryset = queryset.filter(approved=True)
        return queryset

    def get_permissions(self):
        """Return permissions appropriate for this request."""
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsEditorOrJournalist()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        """Update for the application."""
        article = self.get_object()
        if request.user.is_journalist and article.author_id != request.user.id:
            return Response(
                {'detail': 'Journalists can only update their own independent articles.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        response = super().update(request, *args, **kwargs)
        if response.status_code < 300 and request.user.is_journalist:
            article.refresh_from_db()
            article.approved = False
            article.save(update_fields=['approved'])
            response.data['approved'] = False
        return response

    def destroy(self, request, *args, **kwargs):
        """Destroy for the application."""
        article = self.get_object()
        if request.user.is_journalist and article.author_id != request.user.id:
            return Response(
                {'detail': 'Journalists can only delete their own independent articles.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class PublisherListAPIView(generics.ListAPIView):
    """Define the PublisherListAPIView class."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class NewsletterListCreateAPIView(generics.ListCreateAPIView):
    """Define the NewsletterListCreateAPIView class."""
    authentication_classes = [TokenAuthentication]
    serializer_class = NewsletterSerializer

    def get_queryset(self):
        """Return the records available to this request."""
        return Newsletter.objects.filter(articles__approved=True).distinct().select_related('author')

    def get_permissions(self):
        """Return permissions appropriate for this request."""
        if self.request.method == 'POST':
            return [IsEditorOrJournalist()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Perform create for the application."""
        serializer.save(author=self.request.user)


class UserListAPIView(generics.ListAPIView):
    """Define the UserListAPIView class."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ApprovedArticleAPIView(APIView):
    """Internal endpoint used by the approval workflow to log approved articles."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsEditor]

    def post(self, request):
        """Post for the application."""
        article_id = request.data.get('article_id')
        if not article_id:
            return Response(
                {'detail': 'article_id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            article = Article.objects.get(pk=article_id, approved=True)
        except Article.DoesNotExist:
            return Response(
                {'detail': 'Approved article was not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        log, created = ApprovedArticleLog.objects.get_or_create(
            article=article,
            defaults={'article_title': article.title},
        )
        serializer = ApprovedArticleLogSerializer(log)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
