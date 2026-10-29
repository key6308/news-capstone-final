"""HTML views and role-based workflows for the news application.

Views handle registration, article submission and review, newsletter
management, and reader subscriptions.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from rest_framework.authtoken.models import Token

from .forms import ArticleForm, NewsletterForm, RegistrationForm, SubscriptionForm
from .models import Article, Newsletter, Publisher, User
from .services import approve_article_and_notify


def role_required(*roles):
    """Restrict a view to signed-in users with one of the specified roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            """Wrapped for the application."""
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def home(request):
    """Show approved articles and newsletters on the home page."""
    articles = Article.objects.filter(approved=True).select_related('author', 'publisher')
    newsletters = Newsletter.objects.filter(articles__approved=True).distinct()
    return render(request, 'news/home.html', {'articles': articles, 'newsletters': newsletters})


def register(request):
    """Register a user, create an API token, and sign them in."""
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
    """Article detail for the application."""
    article = get_object_or_404(Article, pk=pk, approved=True)
    return render(request, 'news/article_detail.html', {'article': article})


@role_required(User.Roles.JOURNALIST)
def article_create(request):
    """Let journalists submit an article for editor approval."""
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
    return render(request, 'news/article_form.html', {'form': form, 'title': 'Submit Article'})


@role_required(User.Roles.EDITOR, User.Roles.JOURNALIST)
def article_edit(request, pk):
    """Article edit for the application."""
    article = get_object_or_404(Article, pk=pk)
    if request.user.is_journalist and article.author_id != request.user.id:
        raise PermissionDenied
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article, user=request.user)
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
    return render(request, 'news/article_form.html', {'form': form, 'title': 'Edit Article'})


@role_required(User.Roles.EDITOR, User.Roles.JOURNALIST)
@require_POST
def article_delete(request, pk):
    """Article delete for the application."""
    article = get_object_or_404(Article, pk=pk)
    if request.user.is_journalist and article.author_id != request.user.id:
        raise PermissionDenied
    article.delete()
    messages.success(request, 'Article deleted.')
    return redirect('home')


@role_required(User.Roles.EDITOR)
def review_articles(request):
    """Show submitted articles waiting for editor review."""
    articles = Article.objects.filter(approved=False).select_related('author', 'publisher')
    return render(request, 'news/review_articles.html', {'articles': articles})


@role_required(User.Roles.EDITOR)
@require_POST
def approve_article(request, pk):
    """Approve article for the application."""
    article = get_object_or_404(Article, pk=pk)
    article, email_count, api_logged = approve_article_and_notify(article, request.user)
    if api_logged:
        messages.success(request, f'Article approved. {email_count} subscriber(s) were emailed.')
    else:
        messages.warning(request, 'Article approved, but API logging failed. Check the server log.')
    return redirect('review_articles')


@login_required
def newsletter_list(request):
    """Newsletter list for the application."""
    newsletters = Newsletter.objects.filter(articles__approved=True).distinct().select_related('author')
    return render(request, 'news/newsletter_list.html', {'newsletters': newsletters})


@role_required(User.Roles.JOURNALIST, User.Roles.EDITOR)
def newsletter_create(request):
    """Newsletter create for the application."""
    if request.method == 'POST':
        form = NewsletterForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter created.')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm(user=request.user)
    return render(request, 'news/newsletter_form.html', {'form': form, 'title': 'Create Newsletter'})


@role_required(User.Roles.EDITOR, User.Roles.JOURNALIST)
def newsletter_edit(request, pk):
    """Newsletter edit for the application."""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.user.is_journalist and newsletter.author_id != request.user.id:
        raise PermissionDenied
    if request.method == 'POST':
        form = NewsletterForm(request.POST, instance=newsletter, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Newsletter updated.')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm(instance=newsletter, user=request.user)
    return render(request, 'news/newsletter_form.html', {'form': form, 'title': 'Edit Newsletter'})


@role_required(User.Roles.EDITOR, User.Roles.JOURNALIST)
@require_POST
def newsletter_delete(request, pk):
    """Newsletter delete for the application."""
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.user.is_journalist and newsletter.author_id != request.user.id:
        raise PermissionDenied
    newsletter.delete()
    messages.success(request, 'Newsletter deleted.')
    return redirect('newsletter_list')


@login_required
def subscriptions(request):
    """Subscriptions for the application."""
    if not request.user.is_reader:
        raise PermissionDenied
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            request.user.subscribed_publishers.set(form.cleaned_data['publishers'])
            request.user.subscribed_journalists.set(form.cleaned_data['journalists'])
            messages.success(request, 'Subscriptions updated.')
            return redirect('subscriptions')
    else:
        form = SubscriptionForm(initial={
            'publishers': request.user.subscribed_publishers.all(),
            'journalists': request.user.subscribed_journalists.all(),
        })
    return render(request, 'news/subscriptions.html', {'form': form})
