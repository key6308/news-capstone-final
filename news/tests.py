"""Application module for the Django news project."""
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import ApprovedArticleLog, Article, Newsletter, Publisher, User


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NewsApiTests(TestCase):
    """Define the NewsApiTests class."""
    def setUp(self):
        """Setup for the application."""
        self.reader = User.objects.create_user(
            username='reader', email='reader@example.com', password='Pass12345!', role=User.Roles.READER
        )
        self.reader2 = User.objects.create_user(
            username='reader2', email='reader2@example.com', password='Pass12345!', role=User.Roles.READER
        )
        self.journalist = User.objects.create_user(
            username='writer', email='writer@example.com', password='Pass12345!', role=User.Roles.JOURNALIST
        )
        self.other_journalist = User.objects.create_user(
            username='otherwriter', email='other@example.com', password='Pass12345!', role=User.Roles.JOURNALIST
        )
        self.editor = User.objects.create_user(
            username='editor', email='editor@example.com', password='Pass12345!', role=User.Roles.EDITOR
        )
        self.publisher = Publisher.objects.create(name='City News')
        self.publisher.journalists.add(self.journalist)
        self.publisher.editors.add(self.editor)
        self.independent = Article.objects.create(
            title='Independent Story', content='Independent content', author=self.journalist, approved=True
        )
        self.other_article = Article.objects.create(
            title='Other Story', content='Other content', author=self.other_journalist, approved=True
        )
        self.publisher_article = Article.objects.create(
            title='Publisher Story', content='Publisher content', publisher=self.publisher, approved=True
        )
        self.reader.subscribed_journalists.add(self.journalist)
        self.reader.subscribed_publishers.add(self.publisher)
        self.client = APIClient()
        self.reader_token = Token.objects.get_or_create(user=self.reader)[0]
        self.writer_token = Token.objects.get_or_create(user=self.journalist)[0]
        self.editor_token = Token.objects.get_or_create(user=self.editor)[0]

    def auth(self, token):
        """Auth for the application."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_unauthenticated_api_is_rejected(self):
        """Test that unauthenticated api is rejected."""
        response = self.client.get(reverse('api_articles'))
        self.assertEqual(response.status_code, 401)

    def test_reader_gets_only_approved_articles(self):
        """Test that reader gets only approved articles."""
        self.auth(self.reader_token)
        Article.objects.create(title='Draft', content='Draft', author=self.journalist, approved=False)
        response = self.client.get(reverse('api_articles'))
        self.assertEqual(response.status_code, 200)
        titles = {item['title'] for item in response.data}
        self.assertNotIn('Draft', titles)

    def test_reader_gets_only_subscribed_content(self):
        """Test that reader gets only subscribed content."""
        self.auth(self.reader_token)
        response = self.client.get(reverse('api_subscribed_articles'))
        self.assertEqual(response.status_code, 200)
        titles = {item['title'] for item in response.data}
        self.assertEqual(titles, {'Independent Story', 'Publisher Story'})
        self.assertNotIn('Other Story', titles)

    def test_non_reader_cannot_get_subscribed_endpoint(self):
        """Test that non reader cannot get subscribed endpoint."""
        self.auth(self.writer_token)
        response = self.client.get(reverse('api_subscribed_articles'))
        self.assertEqual(response.status_code, 403)

    def test_journalist_can_create_article(self):
        """Test that journalist can create article."""
        self.auth(self.writer_token)
        response = self.client.post(
            reverse('api_articles'),
            {'title': 'New Story', 'content': 'New content'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        article = Article.objects.get(title='New Story')
        self.assertEqual(article.author, self.journalist)
        self.assertFalse(article.approved)

    def test_reader_cannot_create_article(self):
        """Test that reader cannot create article."""
        self.auth(self.reader_token)
        response = self.client.post(
            reverse('api_articles'),
            {'title': 'Not Allowed', 'content': 'Nope'},
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    def test_journalist_cannot_modify_another_journalists_article(self):
        """Test that journalist cannot modify another journalists article."""
        self.auth(self.writer_token)
        response = self.client.delete(
            reverse('api_article_detail', args=[self.other_article.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_editor_can_update_and_delete_article(self):
        """Test that editor can update and delete article."""
        self.auth(self.editor_token)
        response = self.client.put(
            reverse('api_article_detail', args=[self.independent.pk]),
            {'title': 'Updated Story', 'content': 'Updated content', 'publisher': None},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(reverse('api_article_detail', args=[self.independent.pk]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Article.objects.filter(pk=self.independent.pk).exists())

    @patch('news.services.requests.post')
    @patch('news.services.send_mail')
    def test_editor_approval_emails_subscriber_and_logs_api(self, mock_send_mail, mock_post):
        """Test that editor approval emails subscriber and logs api."""
        draft = Article.objects.create(
            title='Needs Approval', content='Draft content', author=self.journalist, approved=False
        )
        mock_post.return_value.raise_for_status.return_value = None
        self.client.force_login(self.editor)
        response = self.client.post(reverse('approve_article', args=[draft.pk]))
        self.assertEqual(response.status_code, 302)
        draft.refresh_from_db()
        self.assertTrue(draft.approved)
        mock_send_mail.assert_called_once()
        mock_post.assert_called_once()
        self.assertTrue(ApprovedArticleLog.objects.filter(article=draft).exists())

    @patch('news.services.requests.post')
    @patch('news.services.send_mail')
    def test_approval_survives_api_logging_failure(self, mock_send_mail, mock_post):
        """Test that approval survives api logging failure."""
        draft = Article.objects.create(
            title='API Failure Story', content='Draft content', author=self.journalist, approved=False
        )
        from requests import RequestException
        mock_post.side_effect = RequestException('network problem')
        self.client.force_login(self.editor)
        response = self.client.post(reverse('approve_article', args=[draft.pk]))
        self.assertEqual(response.status_code, 302)
        draft.refresh_from_db()
        self.assertTrue(draft.approved)
        mock_send_mail.assert_called_once()

    def test_newsletter_can_be_created_by_journalist(self):
        """Test that newsletter can be created by journalist."""
        self.client.force_login(self.journalist)
        response = self.client.post(
            reverse('newsletter_create'),
            {'title': 'Weekly', 'description': 'Weekly stories', 'articles': [self.independent.pk]},
        )
        self.assertEqual(response.status_code, 302)
        newsletter = Newsletter.objects.get(title='Weekly')
        self.assertEqual(newsletter.author, self.journalist)
        self.assertIn(self.independent, newsletter.articles.all())

    def test_reader_cannot_create_newsletter(self):
        """Test that reader cannot create newsletter."""
        self.client.force_login(self.reader)
        response = self.client.get(reverse('newsletter_create'))
        self.assertEqual(response.status_code, 403)

    def test_role_groups_are_assigned(self):
        """Test that role groups are assigned."""
        self.assertTrue(self.reader.groups.filter(name='Reader').exists())
        self.assertTrue(self.journalist.groups.filter(name='Journalist').exists())
        self.assertTrue(self.editor.groups.filter(name='Editor').exists())

    def test_login_works_for_custom_user(self):
        """Test that login works for custom user."""
        response = self.client.post(
            reverse('login'), {'username': 'reader', 'password': 'Pass12345!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
