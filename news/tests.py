"""Automated tests for the news app's web views, REST API, and workflows."""
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import ApprovedArticleLog, Article, Newsletter, Publisher, User

PASSWORD = 'Pass12345!'


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class NewsApiTests(TestCase):
    """Tests for roles, articles, approval, newsletters, and the REST API."""

    def setUp(self):
        """Create users of every role, a publisher, articles, and tokens."""
        self.reader = self.make_user('reader', User.Roles.READER)
        self.reader2 = self.make_user('reader2', User.Roles.READER)
        self.journalist = self.make_user('writer', User.Roles.JOURNALIST)
        self.other_journalist = self.make_user(
            'otherwriter', User.Roles.JOURNALIST
        )
        self.editor = self.make_user('editor', User.Roles.EDITOR)
        self.publisher = Publisher.objects.create(name='City News')
        self.publisher.journalists.add(self.journalist)
        self.publisher.editors.add(self.editor)
        self.other_publisher = Publisher.objects.create(name='Other News')
        self.independent = Article.objects.create(
            title='Independent Story',
            content='Independent content',
            author=self.journalist,
            approved=True,
        )
        self.other_article = Article.objects.create(
            title='Other Story',
            content='Other content',
            author=self.other_journalist,
            approved=True,
        )
        self.publisher_article = Article.objects.create(
            title='Publisher Story',
            content='Publisher content',
            publisher=self.publisher,
            approved=True,
        )
        self.reader.subscribed_journalists.add(self.journalist)
        self.reader.subscribed_publishers.add(self.publisher)
        self.client = APIClient()
        self.reader_token = Token.objects.get_or_create(user=self.reader)[0]
        self.writer_token = Token.objects.get_or_create(
            user=self.journalist
        )[0]
        self.editor_token = Token.objects.get_or_create(user=self.editor)[0]

    @staticmethod
    def make_user(username, role):
        """Create a user with the shared test password and the given role."""
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password=PASSWORD,
            role=role,
        )

    def auth(self, token):
        """Send ``token`` in the Authorization header of later API calls."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # -- REST API: reading ---------------------------------------------------

    def test_unauthenticated_api_is_rejected(self):
        """Test that unauthenticated api is rejected."""
        response = self.client.get(reverse('api_articles'))
        self.assertEqual(response.status_code, 401)

    def test_reader_gets_only_approved_articles(self):
        """Test that reader gets only approved articles."""
        self.auth(self.reader_token)
        Article.objects.create(
            title='Draft', content='Draft', author=self.journalist,
            approved=False,
        )
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

    def test_user_list_hides_other_users_emails(self):
        """Test that /api/users/ shows an email only for the caller's own."""
        self.auth(self.reader_token)
        response = self.client.get(reverse('api_users'))
        self.assertEqual(response.status_code, 200)
        by_id = {item['id']: item for item in response.data}
        self.assertEqual(
            by_id[self.reader.pk]['email'], 'reader@example.com'
        )
        self.assertNotIn('email', by_id[self.journalist.pk])
        self.assertNotIn('email', by_id[self.editor.pk])

    # -- REST API: writing ---------------------------------------------------

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
        url = reverse('api_article_detail', args=[self.other_article.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        response = self.client.patch(
            url, {'title': 'Hijacked'}, format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_editor_can_update_and_delete_article(self):
        """Test that editor can update and delete article."""
        self.auth(self.editor_token)
        url = reverse('api_article_detail', args=[self.independent.pk])
        response = self.client.put(
            url,
            {
                'title': 'Updated Story',
                'content': 'Updated content',
                'publisher': None,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Article.objects.filter(pk=self.independent.pk).exists()
        )

    def test_journalist_update_resets_approval(self):
        """Test that a journalist's API update sends the article back."""
        self.auth(self.writer_token)
        response = self.client.patch(
            reverse('api_article_detail', args=[self.independent.pk]),
            {'title': 'Edited Story'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['approved'])
        self.independent.refresh_from_db()
        self.assertEqual(self.independent.title, 'Edited Story')
        self.assertFalse(self.independent.approved)

    def test_journalist_patch_with_unaffiliated_publisher_is_rejected(self):
        """Test that PATCH runs the publisher affiliation check (400)."""
        self.auth(self.writer_token)
        response = self.client.patch(
            reverse('api_article_detail', args=[self.independent.pk]),
            {'publisher': self.other_publisher.pk},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.independent.refresh_from_db()
        self.assertIsNone(self.independent.publisher)
        self.assertEqual(self.independent.author, self.journalist)

    def test_journalist_patch_moves_article_to_affiliated_publisher(self):
        """Test that setting a publisher on PATCH clears the author."""
        self.auth(self.writer_token)
        response = self.client.patch(
            reverse('api_article_detail', args=[self.independent.pk]),
            {'publisher': self.publisher.pk},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.independent.refresh_from_db()
        self.assertEqual(self.independent.publisher, self.publisher)
        self.assertIsNone(self.independent.author)
        self.assertFalse(self.independent.approved)

    def test_editor_put_publisher_on_independent_article(self):
        """Test that PUT with a publisher no longer fails with HTTP 500."""
        self.auth(self.editor_token)
        response = self.client.put(
            reverse('api_article_detail', args=[self.independent.pk]),
            {
                'title': 'Moved Story',
                'content': 'Moved content',
                'publisher': self.publisher.pk,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.independent.refresh_from_db()
        self.assertEqual(self.independent.publisher, self.publisher)
        self.assertIsNone(self.independent.author)

    def test_update_leaving_article_without_owner_returns_400(self):
        """Test that removing the only owner returns 400, not HTTP 500."""
        self.auth(self.editor_token)
        response = self.client.patch(
            reverse('api_article_detail', args=[self.publisher_article.pk]),
            {'publisher': None},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.publisher_article.refresh_from_db()
        self.assertEqual(self.publisher_article.publisher, self.publisher)

    # -- Approval workflow ---------------------------------------------------

    @patch('news.services.requests.post')
    @patch('news.services.send_mail')
    def test_editor_approval_emails_subscriber_and_logs_api(
        self, mock_send_mail, mock_post
    ):
        """Test that editor approval emails subscriber and logs api."""
        draft = Article.objects.create(
            title='Needs Approval', content='Draft content',
            author=self.journalist, approved=False,
        )
        mock_post.return_value.raise_for_status.return_value = None
        self.client.force_login(self.editor)
        response = self.client.post(
            reverse('approve_article', args=[draft.pk])
        )
        self.assertEqual(response.status_code, 302)
        draft.refresh_from_db()
        self.assertTrue(draft.approved)
        mock_send_mail.assert_called_once()
        mock_post.assert_called_once()
        self.assertEqual(
            mock_post.call_args.kwargs['json'], {'article_id': draft.pk}
        )

    @patch('news.services.requests.post')
    @patch('news.services.send_mail')
    def test_approval_survives_api_logging_failure(
        self, mock_send_mail, mock_post
    ):
        """Test that approval survives api logging failure."""
        draft = Article.objects.create(
            title='API Failure Story', content='Draft content',
            author=self.journalist, approved=False,
        )
        from requests import RequestException
        mock_post.side_effect = RequestException('network problem')
        self.client.force_login(self.editor)
        with self.assertLogs('news.services', level='WARNING'):
            response = self.client.post(
                reverse('approve_article', args=[draft.pk])
            )
        self.assertEqual(response.status_code, 302)
        draft.refresh_from_db()
        self.assertTrue(draft.approved)
        mock_send_mail.assert_called_once()

    def test_approved_api_creates_log_entry(self):
        """Test that POST /api/approved/ creates an ApprovedArticleLog."""
        self.auth(self.editor_token)
        url = reverse('api_approved')
        payload = {'article_id': self.independent.pk}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            ApprovedArticleLog.objects.filter(
                article=self.independent
            ).exists()
        )
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 200)

    def test_approved_api_rejects_non_numeric_article_id(self):
        """Test that a non-numeric article_id returns 400, not HTTP 500."""
        self.auth(self.editor_token)
        response = self.client.post(
            reverse('api_approved'), {'article_id': 'abc'}, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('integer', response.data['detail'])
        self.assertFalse(ApprovedArticleLog.objects.exists())

    def test_approved_api_is_editor_only(self):
        """Test that non-editors cannot write approval log entries."""
        self.auth(self.writer_token)
        response = self.client.post(
            reverse('api_approved'),
            {'article_id': self.independent.pk},
            format='json',
        )
        self.assertEqual(response.status_code, 403)

    # -- Web pages -----------------------------------------------------------

    def test_journalist_can_submit_independent_article_via_form(self):
        """Test that /articles/new/ without a publisher saves the article."""
        self.client.force_login(self.journalist)
        response = self.client.post(
            reverse('article_create'),
            {'title': 'Web Story', 'content': 'Web content', 'publisher': ''},
        )
        self.assertEqual(response.status_code, 302)
        article = Article.objects.get(title='Web Story')
        self.assertEqual(article.author, self.journalist)
        self.assertIsNone(article.publisher)
        self.assertFalse(article.approved)

    def test_journalist_can_submit_publisher_article_via_form(self):
        """Test that /articles/new/ with a publisher saves a publisher one."""
        self.client.force_login(self.journalist)
        response = self.client.post(
            reverse('article_create'),
            {
                'title': 'Web Publisher Story',
                'content': 'Web content',
                'publisher': self.publisher.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        article = Article.objects.get(title='Web Publisher Story')
        self.assertIsNone(article.author)
        self.assertEqual(article.publisher, self.publisher)

    def test_journalist_cannot_submit_for_unaffiliated_publisher(self):
        """Test that the form rejects a publisher the journalist lacks."""
        self.client.force_login(self.journalist)
        response = self.client.post(
            reverse('article_create'),
            {
                'title': 'Sneaky Story',
                'content': 'Web content',
                'publisher': self.other_publisher.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Article.objects.filter(title='Sneaky Story').exists())

    def test_home_edit_link_only_for_owner_or_editor(self):
        """Test that Edit links appear only for the author or an editor."""
        def edit_url(article):
            """Return the edit-page URL of ``article``."""
            return reverse('article_edit', args=[article.pk])

        self.client.force_login(self.journalist)
        page = self.client.get(reverse('home')).content.decode()
        self.assertIn(edit_url(self.independent), page)
        self.assertNotIn(edit_url(self.other_article), page)
        self.assertNotIn(edit_url(self.publisher_article), page)

        self.client.force_login(self.editor)
        page = self.client.get(reverse('home')).content.decode()
        for article in (
            self.independent, self.other_article, self.publisher_article
        ):
            self.assertIn(edit_url(article), page)

        self.client.force_login(self.reader)
        page = self.client.get(reverse('home')).content.decode()
        self.assertNotIn('/edit/', page)

    def test_registration_offers_reader_and_journalist_only(self):
        """Test that visitors cannot register themselves as editors."""
        data = {
            'username': 'newbie',
            'email': 'newbie@example.com',
            'password1': 'S3cure-Passw0rd!',
            'password2': 'S3cure-Passw0rd!',
        }
        response = self.client.post(
            reverse('register'), {**data, 'role': User.Roles.EDITOR}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newbie').exists())

        response = self.client.post(
            reverse('register'), {**data, 'role': User.Roles.JOURNALIST}
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newbie')
        self.assertTrue(user.is_journalist)

    def test_newsletter_can_be_created_by_journalist(self):
        """Test that newsletter can be created by journalist."""
        self.client.force_login(self.journalist)
        response = self.client.post(
            reverse('newsletter_create'),
            {
                'title': 'Weekly',
                'description': 'Weekly stories',
                'articles': [self.independent.pk],
            },
        )
        self.assertEqual(response.status_code, 302)
        newsletter = Newsletter.objects.get(title='Weekly')
        self.assertEqual(newsletter.author, self.journalist)
        self.assertIn(self.independent, newsletter.articles.all())

    def test_newsletter_list_shows_approved_articles(self):
        """Test that the newsletter list renders its approved articles."""
        newsletter = Newsletter.objects.create(
            title='Digest', author=self.editor
        )
        newsletter.articles.add(self.independent)
        self.client.force_login(self.reader)
        response = self.client.get(reverse('newsletter_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Digest')
        self.assertContains(response, 'Independent Story')

    def test_reader_cannot_create_newsletter(self):
        """Test that reader cannot create newsletter."""
        self.client.force_login(self.reader)
        response = self.client.get(reverse('newsletter_create'))
        self.assertEqual(response.status_code, 403)

    # -- Accounts and permission groups --------------------------------------

    def test_role_groups_are_assigned(self):
        """Test that role groups are assigned."""
        self.assertTrue(self.reader.groups.filter(name='Reader').exists())
        self.assertTrue(
            self.journalist.groups.filter(name='Journalist').exists()
        )
        self.assertTrue(self.editor.groups.filter(name='Editor').exists())

    def test_role_group_rebuilt_only_when_role_changes(self):
        """Test that saves without a role change leave the groups alone."""
        user = User.objects.get(pk=self.reader.pk)
        user.groups.clear()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        user.first_name = 'Rita'
        user.save()
        self.assertFalse(user.groups.exists())

        user.role = User.Roles.EDITOR
        user.save()
        self.assertEqual(
            list(user.groups.values_list('name', flat=True)), ['Editor']
        )

    def test_login_works_for_custom_user(self):
        """Test that login works for custom user."""
        response = self.client.post(
            reverse('login'), {'username': 'reader', 'password': PASSWORD}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
