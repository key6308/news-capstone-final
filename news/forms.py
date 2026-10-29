"""Validated HTML forms for the news application.

The forms restrict choices according to the signed-in user role and provide
cleaned data to the corresponding views.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, Newsletter, Publisher, User


class RegistrationForm(UserCreationForm):
    """Collect the details needed to create an application account."""
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.Roles.choices)

    class Meta:
        """Define the Meta class."""
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')


class ArticleForm(forms.ModelForm):
    """Validate article fields and enforce journalist publisher affiliations."""
    class Meta:
        """Define the Meta class."""
        model = Article
        fields = ('title', 'content', 'publisher')
        widgets = {'content': forms.Textarea(attrs={'rows': 8})}

    def __init__(self, *args, user=None, **kwargs):
        """Initialize this object."""
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_journalist:
            self.fields['publisher'].queryset = user.journalist_publishers.all()
            self.fields['publisher'].required = False

    def clean(self):
        """Validate clean data."""
        cleaned = super().clean()
        publisher = cleaned.get('publisher')
        if self.user and self.user.is_journalist and publisher:
            if not publisher.journalists.filter(pk=self.user.pk).exists():
                raise forms.ValidationError('You are not affiliated with this publisher.')
            # A journalist may publish independently or on behalf of a publisher.
            cleaned['author'] = None
        elif self.user and self.user.is_journalist:
            cleaned['author'] = self.user
        return cleaned


class NewsletterForm(forms.ModelForm):
    """Define the NewsletterForm class."""
    class Meta:
        """Define the Meta class."""
        model = Newsletter
        fields = ('title', 'description', 'articles')
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, user=None, **kwargs):
        """Initialize this object."""
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['articles'].queryset = Article.objects.filter(approved=True)

    def save(self, commit=True):
        """Save for the application."""
        newsletter = super().save(commit=False)
        if not newsletter.pk:
            newsletter.author = self.user
        if commit:
            newsletter.save()
            self.save_m2m()
        return newsletter


class SubscriptionForm(forms.Form):
    """Collect publisher and journalist subscription choices."""
    publishers = forms.ModelMultipleChoiceField(
        queryset=Publisher.objects.all(), required=False
    )
    journalists = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role=User.Roles.JOURNALIST), required=False
    )
