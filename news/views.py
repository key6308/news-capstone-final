"""HTML views and role-based workflows for the news application.

Views handle registration, article submission and review, newsletter
management, and reader subscriptions.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from rest_framework.authtoken.models import Token

from .forms import (
    ArticleForm,
    NewsletterForm,
    RegistrationForm,
    SubscriptionForm,
)
from .models import Article, Newsletter, User
from .services import approve_article_and_notify


def role_required(*roles):
    """Restrict a view to signed-in users with one of the specified roles.

    Anonymous users are redirected to the login page. Signed-in users with a
    different role receive *403 Forbidden*.

    Args:
        *roles (str): Allowed values from :class:`news.models.User.Roles`.

    Returns:
        Callable: A decorator to apply to a view function.

    Example:
        .. code-block:: python

            @role_required(User.Roles.EDITOR)
            def review_articles(request):
                ...
    """
    def decorator(view_func):
        """Wrap ``view_func`` with the sign-in and role check."""
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            """Check the user's role, then call the wrapped view."""
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def home(request):
    """Show approved articles on the home page.

    URL: ``/``. Available to everyone.
    """
    articles = Article.objects.filter(approved=True).select_related(
        'author', 'publisher'
    )
    return render(request, 'news/home.html', {'articles': articles})


def register(request):
    """Register a user, create an API token, and sign them in.

    URL: ``/register/``. Available to everyone.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Token.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Your account was created.')
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'news/register.html', {'form': form})


@login_required
def article_detail(request, pk):
    """Show one approved article.

    URL: ``/articles/<pk>/``. Requires sign-in. Unapproved articles return
    *404 Not Found*.
    """
    article = get_object_or_404(Article, pk=pk, approved=True)
    return render(request, 'news/article_detail.html', {'article': article})


@role_required(User.Roles.JOURNALIST)
def article_create(request):
    """Let journalists submit an article for editor approval.

    URL: ``/articles/new/``. Journalists only.
    """
    if request.method == 'POST':
        form = ArticleForm(request.POST, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = None if article.publisher_id else request.user
            article.approved = False
            article.full_clean()
            article.save()
            messages.success(request, 'Article submitted for editor approval.')
            return redirect('home')
    else:
        form = ArticleForm(user=request.user)
    return render(
        request,
        'news/article_form.html',
        {'form': form, 'title': 'Submit Article'},
    )


@role_required(User.Roles.EDITOR, User.Roles.JOURNALIST)
def article_edit(request, pk):
    """Edit an article.

    URL: ``/articles/<pk>/edit/``. Editors can edit any article; journalists
    can edit only their own independent articles. A journalist's edit sends
    the article back for approval.
    """
    article = get_object_or_404(Article, pk=pk)
    if not request.user.can_modify(article):
        raise PermissionDenied
    if request.method == 'POST':
        form = ArticleForm(
            request.POST, instance=article, user=request.user
        )
        if form.is_valid():
            article = form.save(commit=False)
            if request.user.is_journalist:
                article.author = None if article.publisher_id else request.user
                article.approved = False
            article.full_clean()
            article.save()
            messages.success(request, 'Article updated.')
            return redirect('home')
    else:
        form = ArticleForm(instance=article, user=request.user)
    return render(
        request,
        'news/article_form.html',
        {'form': form, 'title': 'Edit Article'},
    )


@role_required(User.Roles.EDITOR, User.Roles.JOURNALIST)
@require_POST
def article_delete(request, pk):
    """Delete an article (POST only).

    URL: ``/articles/<pk>/delete/``. Editors can delete any article;
    journalists can delete only their own independent articles.
    """
    article = get_object_or_404(Article, pk=pk)
    if not request.user.can_modify(article):
        raise PermissionDenied
    article.delete()
    messages.success(request, 'Article deleted.')
    return redirect('home')


@role_required(User.Roles.EDITOR)
def review_articles(request):
    """Show submitted articles waiting for editor review.

    URL: ``/editor/review/``. Editors only.
    """
    articles = Article.objects.filter(approved=False).select_related(
        'author', 'publisher'
    )
    return render(
        request, 'news/review_articles.html', {'articles': articles}
    )


@role_required(User.Roles.EDITOR)
@require_POST
def approve_article(request, pk):
    """Approve an article, email subscribers, and log the approval (POST only).

    URL: ``/editor/articles/<pk>/approve/``. Editors only. See
    :func:`news.services.approve_article_and_notify`.
    """
    article = get_object_or_404(Article, pk=pk)
    article, email_count, api_logged = approve_article_and_notify(
        article, request.user
    )
    if api_logged:
        messages.success(
            request,
            f'Article approved. {email_count} subscriber(s) were emailed.',
        )
    else:
        messages.warning(
            request,
            'Article approved, but API logging failed. Check the server log.',
        )
    return redirect('review_articles')


@login_required
def newsletter_list(request):
    """List newsletters that contain approved articles.

    URL: ``/newsletters/``. Requires sign-in.
    """
    newsletters = (
        Newsletter.objects.filter(articles__approved=True)
        .distinct()
        .select_related('author')
        .prefetch_related('articles')
    )
    return render(
        request, 'news/newsletter_list.html', {'newsletters': newsletters}
    )


@role_required(User.Roles.JOURNALIST, User.Roles.EDITOR)
def newsletter_create(request):
    """Create a newsletter.

    URL: ``/newsletters/new/``. Journalists and editors only.
    """
    if request.method == 'POST':
        form = NewsletterForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter created.')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm(user=request.user)
    return render(
        request,
        'news/newsletter_form.html',
        {'form': form, 'title': 'Create Newsletter'},
    )


@role_required(User.Roles.EDITOR, User.Roles.JOURNALIST)
def newsletter_edit(request, pk):
    """Edit a newsletter.

    URL: ``/newsletters/<pk>/edit/``. Editors can edit any newsletter;
    journalists can edit only their own.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if not request.user.can_modify(newsletter):
        raise PermissionDenied
    if request.method == 'POST':
        form = NewsletterForm(
            request.POST, instance=newsletter, user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter updated.')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm(instance=newsletter, user=request.user)
    return render(
        request,
        'news/newsletter_form.html',
        {'form': form, 'title': 'Edit Newsletter'},
    )


@role_required(User.Roles.EDITOR, User.Roles.JOURNALIST)
@require_POST
def newsletter_delete(request, pk):
    """Delete a newsletter (POST only).

    URL: ``/newsletters/<pk>/delete/``. Editors can delete any newsletter;
    journalists can delete only their own.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if not request.user.can_modify(newsletter):
        raise PermissionDenied
    newsletter.delete()
    messages.success(request, 'Newsletter deleted.')
    return redirect('newsletter_list')


@login_required
def subscriptions(request):
    """Let a reader view and update their subscriptions.

    URL: ``/subscriptions/``. Readers only.
    """
    if not request.user.is_reader:
        raise PermissionDenied
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            request.user.subscribed_publishers.set(
                form.cleaned_data['publishers']
            )
            request.user.subscribed_journalists.set(
                form.cleaned_data['journalists']
            )
            messages.success(request, 'Subscriptions updated.')
            return redirect('subscriptions')
    else:
        form = SubscriptionForm(initial={
            'publishers': request.user.subscribed_publishers.all(),
            'journalists': request.user.subscribed_journalists.all(),
        })
    return render(request, 'news/subscriptions.html', {'form': form})
