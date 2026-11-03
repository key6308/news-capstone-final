"""REST API endpoints for news content and subscriptions.

Endpoints apply authentication and role-based permissions before returning or
changing application data.
"""

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from news.models import (
    ApprovedArticleLog,
    Article,
    Newsletter,
    Publisher,
    User,
)

from .permissions import IsEditor, IsEditorOrJournalist, IsJournalist, IsReader
from .serializers import (
    ApprovedArticleLogSerializer,
    ArticleSerializer,
    NewsletterSerializer,
    PublisherSerializer,
    UserSerializer,
)


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """List approved articles or submit a new article.

    * ``GET /api/articles/`` -- any signed-in user.
    * ``POST /api/articles/`` -- journalists only.
    """
    authentication_classes = [TokenAuthentication]
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """Require a journalist for POST and any signed-in user otherwise."""
        if self.request.method == 'POST':
            return [IsJournalist()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Return approved articles only."""
        return Article.objects.filter(approved=True).select_related(
            'author', 'publisher'
        )


class SubscribedArticleListAPIView(generics.ListAPIView):
    """List approved articles from the reader's subscriptions.

    * ``GET /api/articles/subscribed/`` -- readers only.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsReader]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """Return approved articles from followed publishers/journalists."""
        user = self.request.user
        return Article.objects.filter(approved=True).filter(
            Q(publisher__in=user.subscribed_publishers.all())
            | Q(author__in=user.subscribed_journalists.all())
        ).distinct().select_related('author', 'publisher')


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete one article.

    * ``GET /api/articles/<pk>/`` -- any signed-in user (approved articles
      only).
    * ``PUT``/``PATCH``/``DELETE`` -- editors, or journalists for their own
      independent articles. A journalist's update sends the article back for
      approval.
    """
    authentication_classes = [TokenAuthentication]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """Return all articles, limited to approved ones for read requests."""
        queryset = Article.objects.select_related('author', 'publisher').all()
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            queryset = queryset.filter(approved=True)
        return queryset

    def get_permissions(self):
        """Require an editor or journalist for changes, sign-in for reads."""
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsEditorOrJournalist()]
        return [IsAuthenticated()]

    def get_object(self):
        """Return the article, checking ownership for changes.

        Raises:
            rest_framework.exceptions.PermissionDenied: If a journalist tries
                to change an article they do not own (*403 Forbidden*).
        """
        article = super().get_object()
        method = self.request.method
        if method in ('PUT', 'PATCH', 'DELETE'):
            if not self.request.user.can_modify(article):
                action = 'delete' if method == 'DELETE' else 'update'
                raise PermissionDenied(
                    f'Journalists can only {action} their own independent '
                    'articles.'
                )
        return article

    def perform_update(self, serializer):
        """Save the update; a journalist's change resets ``approved``."""
        if self.request.user.is_journalist:
            serializer.save(approved=False)
        else:
            serializer.save()


class PublisherListAPIView(generics.ListAPIView):
    """List publishers.

    * ``GET /api/publishers/`` -- any signed-in user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class NewsletterListCreateAPIView(generics.ListCreateAPIView):
    """List newsletters or create a new one.

    * ``GET /api/newsletters/`` -- any signed-in user.
    * ``POST /api/newsletters/`` -- editors and journalists.
    """
    authentication_classes = [TokenAuthentication]
    serializer_class = NewsletterSerializer

    def get_queryset(self):
        """Return newsletters that contain at least one approved article."""
        return (
            Newsletter.objects.filter(articles__approved=True)
            .distinct()
            .select_related('author')
        )

    def get_permissions(self):
        """Require an editor or journalist for POST and sign-in otherwise."""
        if self.request.method == 'POST':
            return [IsEditorOrJournalist()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Save the new newsletter with the requesting user as author."""
        serializer.save(author=self.request.user)


class UserListAPIView(generics.ListAPIView):
    """List users.

    * ``GET /api/users/`` -- any signed-in user. Email addresses are only
      included in the requesting user's own record.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ApprovedArticleAPIView(APIView):
    """Internal endpoint used by the approval workflow to log approvals.

    ``POST /api/approved/`` with ``{"article_id": <id>}`` -- editors only.
    Called by :func:`news.services.post_approved_article`.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsEditor]

    def post(self, request):
        """Create the log entry for an approved article.

        Returns:
            rest_framework.response.Response: ``201`` with the new log entry,
            ``200`` if it already existed, ``400`` if ``article_id`` is
            missing or not an integer, or ``404`` if no approved article has
            that ID.
        """
        article_id = request.data.get('article_id')
        if not article_id:
            return Response(
                {'detail': 'article_id is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            article_id = int(article_id)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'article_id must be an integer.'},
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
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
