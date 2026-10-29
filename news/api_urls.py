"""Application module for the Django news project."""
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
    path('articles/subscribed/', SubscribedArticleListAPIView.as_view(), name='api_subscribed_articles'),
    path('articles/<int:pk>/', ArticleDetailAPIView.as_view(), name='api_article_detail'),
    path('publishers/', PublisherListAPIView.as_view(), name='api_publishers'),
    path('newsletters/', NewsletterListCreateAPIView.as_view(), name='api_newsletters'),
    path('users/', UserListAPIView.as_view(), name='api_users'),
    path('approved/', ApprovedArticleAPIView.as_view(), name='api_approved'),
]
