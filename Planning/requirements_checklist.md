# Capstone Requirements Checklist

This checklist maps the task PDF requirements to the project files.

| Requirement | Implementation |
|---|---|
| New Django project/app | `news_application/`, `news/`, `manage.py` |
| Article fields title/content/author/created_at/approved/publisher | `news/models.py` → `Article` |
| Article associated with journalist OR publisher | `Article` check constraint + `clean()` |
| Publisher has editors/journalists | `Publisher.editors`, `Publisher.journalists` |
| Newsletter with title/description/created_at/author/M2M Article | `Newsletter` model |
| Readers can view newsletters | `newsletter_list` + template |
| Journalists/editors create and edit newsletters | newsletter create/edit views + role checks |
| Custom user | `news.User` extends `AbstractUser` |
| Reader/editor/journalist roles | `User.Roles` |
| Role-based groups | `news/signals.py` |
| Reader publisher/journalist subscriptions | User M2M fields |
| Journalist independent article/newsletter relations | `User.independent_articles`, `User.newsletters` |
| Reader fields not used for journalists | role checks + empty M2M subscriptions; documented in model design |
| Editor article review/approval | `review_articles`, `approve_article` |
| Access control | web role decorator + DRF permission classes |
| Email subscribers after approval | `news/services.py` |
| POST approved article to own API | `post_approved_article()` using `requests` |
| GET `/api/articles/` | `ArticleListCreateAPIView` |
| GET `/api/articles/subscribed/` | `SubscribedArticleListAPIView` |
| GET `/api/articles/<id>/` | `ArticleDetailAPIView` |
| POST `/api/articles/` journalists only | `IsJournalist` |
| PUT/PATCH article | `IsEditorOrJournalist` + ownership check |
| DELETE article | `IsEditorOrJournalist` + ownership check |
| Token authentication | DRF TokenAuthentication + `/api/token/` |
| Only journalists POST | permission class |
| Only editors approve | web role + internal API permission |
| Readers view only | reader permissions and read-only API behavior |
| DRF serializers for Article/User/Newsletter/Publisher | `news/api/serializers.py` |
| Automated unit tests | `news/tests.py` |
| Successful + failed requests | tests include 401/403 and successful 200/201/204 flows |
| Subscription filtering tests | `test_reader_gets_only_subscribed_content` |
| Approval/email/API integration tests | mocked `send_mail` and `requests.post` |
| MariaDB | MySQL backend configured for MariaDB in `settings.py` |
| PEP 8/readable/modular/defensive | modular services, validation, exception handling, comments/docstrings |
| Planning/UI/UX | `Planning/` |
| Normalized data model | `Planning/data_model.md` |
| Sequence diagram | `Planning/sequence_diagram.svg` |
