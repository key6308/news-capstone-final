"""URL routes for the token-authenticated REST API (mounted at ``/api/``).

.. list-table::
   :header-rows: 1

   * - Path
     - Name
     - View
   * - ``/api/token/``
     - ``api_token``
     - DRF ``obtain_auth_token`` (username/password to token)
   * - ``/api/articles/``
     - ``api_articles``
     - :class:`news.api.views.ArticleListCreateAPIView`
   * - ``/api/articles/subscribed/``
     - ``api_subscribed_articles``
     - :class:`news.api.views.SubscribedArticleListAPIView`
   * - ``/api/articles/<pk>/``
     - ``api_article_detail``
     - :class:`news.api.views.ArticleDetailAPIView`
   * - ``/api/publishers/``
     - ``api_publishers``
     - :class:`news.api.views.PublisherListAPIView`
   * - ``/api/newsletters/``
     - ``api_newsletters``
     - :class:`news.api.views.NewsletterListCreateAPIView`
   * - ``/api/users/``
     - ``api_users``
     - :class:`news.api.views.UserListAPIView`
   * - ``/api/approved/``
     - ``api_approved``
     - :class:`news.api.views.ApprovedArticleAPIView`
"""
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .api.views import (
    ApprovedArticleAPIView,
    ArticleDetailAPIView,
    ArticleListCreateAPIView,
    NewsletterListCreateAPIView,
    PublisherListAPIView,
    SubscribedArticleListAPIView,
    UserListAPIView,
)

urlpatterns = [
    path('token/', obtain_auth_token, name='api_token'),
    path('articles/', ArticleListCreateAPIView.as_view(), name='api_articles'),
    path(
        'articles/subscribed/',
        SubscribedArticleListAPIView.as_view(),
        name='api_subscribed_articles',
    ),
    path(
        'articles/<int:pk>/',
        ArticleDetailAPIView.as_view(),
        name='api_article_detail',
    ),
    path('publishers/', PublisherListAPIView.as_view(), name='api_publishers'),
    path(
        'newsletters/',
        NewsletterListCreateAPIView.as_view(),
        name='api_newsletters',
    ),
    path('users/', UserListAPIView.as_view(), name='api_users'),
    path('approved/', ApprovedArticleAPIView.as_view(), name='api_approved'),
]
