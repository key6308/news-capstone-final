"""URL routes for the HTML pages of the ``news`` app.

These routes are included at the site root by ``news_application/urls.py``,
which also adds ``/admin/``, ``/login/``, ``/logout/``, and ``/api/``.

.. list-table::
   :header-rows: 1

   * - Path
     - Name
     - View
   * - ``/``
     - ``home``
     - :func:`news.views.home`
   * - ``/register/``
     - ``register``
     - :func:`news.views.register`
   * - ``/articles/<pk>/``
     - ``article_detail``
     - :func:`news.views.article_detail`
   * - ``/articles/new/``
     - ``article_create``
     - :func:`news.views.article_create`
   * - ``/articles/<pk>/edit/``
     - ``article_edit``
     - :func:`news.views.article_edit`
   * - ``/articles/<pk>/delete/``
     - ``article_delete``
     - :func:`news.views.article_delete`
   * - ``/editor/review/``
     - ``review_articles``
     - :func:`news.views.review_articles`
   * - ``/editor/articles/<pk>/approve/``
     - ``approve_article``
     - :func:`news.views.approve_article`
   * - ``/newsletters/``
     - ``newsletter_list``
     - :func:`news.views.newsletter_list`
   * - ``/newsletters/new/``
     - ``newsletter_create``
     - :func:`news.views.newsletter_create`
   * - ``/newsletters/<pk>/edit/``
     - ``newsletter_edit``
     - :func:`news.views.newsletter_edit`
   * - ``/newsletters/<pk>/delete/``
     - ``newsletter_delete``
     - :func:`news.views.newsletter_delete`
   * - ``/subscriptions/``
     - ``subscriptions``
     - :func:`news.views.subscriptions`
"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/new/', views.article_create, name='article_create'),
    path('articles/<int:pk>/edit/', views.article_edit, name='article_edit'),
    path(
        'articles/<int:pk>/delete/',
        views.article_delete,
        name='article_delete',
    ),
    path('editor/review/', views.review_articles, name='review_articles'),
    path(
        'editor/articles/<int:pk>/approve/',
        views.approve_article,
        name='approve_article',
    ),
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path(
        'newsletters/new/',
        views.newsletter_create,
        name='newsletter_create',
    ),
    path(
        'newsletters/<int:pk>/edit/',
        views.newsletter_edit,
        name='newsletter_edit',
    ),
    path(
        'newsletters/<int:pk>/delete/',
        views.newsletter_delete,
        name='newsletter_delete',
    ),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
]
