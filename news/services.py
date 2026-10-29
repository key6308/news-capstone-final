"""Business services for article approval and notifications.

The service layer keeps approval, subscriber email, and external API logging
logic out of the request-handling views.
"""

import logging
import os

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from rest_framework.authtoken.models import Token

from .models import ApprovedArticleLog, Article

logger = logging.getLogger(__name__)


def get_article_subscriber_emails(article):
    """Return unique email addresses for readers subscribed to the article owner."""
    if article.publisher_id:
        subscribers = article.publisher.subscriber_users.filter(is_active=True, role='reader')
    elif article.author_id:
        subscribers = article.author.journalist_subscribers.filter(is_active=True, role='reader')
    else:
        subscribers = []
    return sorted({user.email for user in subscribers if user.email})


def email_approved_article(article):
    """Email an approved article to its subscribers and return recipient count."""
    recipients = get_article_subscriber_emails(article)
    if not recipients:
        return 0
    send_mail(
        subject=f'New approved article: {article.title}',
        message=article.content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )
    return len(recipients)


def post_approved_article(article, token):
    """Post the approved article ID to the configured API endpoint."""
    url = os.getenv('APPROVED_API_URL', settings.APPROVED_API_URL)
    response = requests.post(
        url,
        json={'article_id': article.pk},
        headers={'Authorization': f'Token {token}'},
        timeout=10,
    )
    response.raise_for_status()
    return response


def approve_article_and_notify(article, editor):
    """Approve once, then email subscribers and log through the project's API."""
    with transaction.atomic():
        article = Article.objects.select_for_update().get(pk=article.pk)
        article.approved = True
        article.save(update_fields=['approved'])

    token, _ = Token.objects.get_or_create(user=editor)
    token = token.key
    email_count = email_approved_article(article)
    try:
        post_approved_article(article, token)
        api_logged = True
    except requests.RequestException as exc:
        logger.warning('Approved article API logging failed: %s', exc)
        api_logged = False

    return article, email_count, api_logged
