"""Validated HTML forms for the news application.

The forms restrict choices according to the signed-in user role and provide
cleaned data to the corresponding views.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, Newsletter, Publisher, User

#: Roles a visitor may choose when registering. Editor accounts are created
#: by an administrator.
PUBLIC_REGISTRATION_ROLES = [
    (User.Roles.READER, User.Roles.READER.label),
    (User.Roles.JOURNALIST, User.Roles.JOURNALIST.label),
]


class RegistrationForm(UserCreationForm):
    """Sign-up form that collects username, email, role, and password.

    Extends Django's :class:`~django.contrib.auth.forms.UserCreationForm`
    with a required email address and a choice of account role. Only the
    reader and journalist roles can be chosen; editors are created by an
    administrator.
    """
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=PUBLIC_REGISTRATION_ROLES)

    class Meta:
        """Build the form from :class:`news.models.User`."""
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')


class ArticleForm(forms.ModelForm):
    """Create or edit an article and enforce journalist publisher affiliations.

    Journalists can only choose publishers they are affiliated with. Leaving
    the publisher empty submits the article as an independent article.

    Args:
        *args: Positional arguments passed to :class:`~django.forms.ModelForm`.
        user (news.models.User, optional): The signed-in user. Used to limit
            the publisher choices and to set the article owner.
        **kwargs: Keyword arguments passed to :class:`~django.forms.ModelForm`.
    """
    class Meta:
        """Build the form from :class:`news.models.Article`."""
        model = Article
        fields = ('title', 'content', 'publisher')
        widgets = {'content': forms.Textarea(attrs={'rows': 8})}

    def __init__(self, *args, user=None, **kwargs):
        """Store the user and restrict publisher choices for journalists."""
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_journalist:
            self.fields['publisher'].queryset = (
                user.journalist_publishers.all()
            )
            self.fields['publisher'].required = False

    def clean(self):
        """Check publisher affiliation and record who owns the article.

        For journalists, the article's ``author`` is set on the form instance
        before model validation runs: the journalist for an independent
        article, or ``None`` for a publisher article.

        Returns:
            dict: The cleaned form data.

        Raises:
            django.forms.ValidationError: If a journalist selects a publisher
                they are not affiliated with.
        """
        cleaned = super().clean()
        publisher = cleaned.get('publisher')
        if self.user and self.user.is_journalist and publisher:
            if not publisher.journalists.filter(pk=self.user.pk).exists():
                raise forms.ValidationError(
                    'You are not affiliated with this publisher.'
                )
        if self.user and self.user.is_journalist:
            # A journalist may publish independently or for a publisher.
            self.instance.author = None if publisher else self.user
        return cleaned


class NewsletterForm(forms.ModelForm):
    """Create or edit a newsletter from approved articles.

    Args:
        *args: Positional arguments passed to :class:`~django.forms.ModelForm`.
        user (news.models.User, optional): The signed-in user, recorded as the
            author of a new newsletter.
        **kwargs: Keyword arguments passed to :class:`~django.forms.ModelForm`.
    """
    class Meta:
        """Build the form from :class:`news.models.Newsletter`."""
        model = Newsletter
        fields = ('title', 'description', 'articles')
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, user=None, **kwargs):
        """Store the user and offer only approved articles."""
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['articles'].queryset = Article.objects.filter(
            approved=True
        )

    def save(self, commit=True):
        """Save the newsletter, setting the author on first save.

        Args:
            commit (bool): If ``True`` (the default), write the newsletter and
                its article selections to the database.

        Returns:
            news.models.Newsletter: The saved (or unsaved) newsletter.
        """
        newsletter = super().save(commit=False)
        if not newsletter.pk:
            newsletter.author = self.user
        if commit:
            newsletter.save()
            self.save_m2m()
        return newsletter


class SubscriptionForm(forms.Form):
    """Let a reader choose the publishers and journalists they follow."""
    publishers = forms.ModelMultipleChoiceField(
        queryset=Publisher.objects.all(), required=False
    )
    journalists = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role=User.Roles.JOURNALIST),
        required=False,
    )
