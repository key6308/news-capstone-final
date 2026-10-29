"""Application module for the Django news project."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/new/', views.article_create, name='article_create'),
    path('articles/<int:pk>/edit/', views.article_edit, name='article_edit'),
    path('articles/<int:pk>/delete/', views.article_delete, name='article_delete'),
    path('editor/review/', views.review_articles, name='review_articles'),
    path('editor/articles/<int:pk>/approve/', views.approve_article, name='approve_article'),
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletters/new/', views.newsletter_create, name='newsletter_create'),
    path('newsletters/<int:pk>/edit/', views.newsletter_edit, name='newsletter_edit'),
    path('newsletters/<int:pk>/delete/', views.newsletter_delete, name='newsletter_delete'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
]
