"""Application module for the Django news project."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ApprovedArticleLog, Article, Newsletter, Publisher, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Define the CustomUserAdmin class."""
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('News application', {
            'fields': ('role', 'subscribed_publishers', 'subscribed_journalists'),
        }),
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Define the PublisherAdmin class."""
    list_display = ('name', 'created_at')
    filter_horizontal = ('editors', 'journalists')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Define the ArticleAdmin class."""
    list_display = ('title', 'article_owner', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('title', 'content')

    @admin.display(description='Owner')
    def article_owner(self, obj):
        """Article owner for the application."""
        return obj.author or obj.publisher


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Define the NewsletterAdmin class."""
    list_display = ('title', 'author', 'created_at')
    filter_horizontal = ('articles',)


@admin.register(ApprovedArticleLog)
class ApprovedArticleLogAdmin(admin.ModelAdmin):
    """Define the ApprovedArticleLogAdmin class."""
    list_display = ('article_title', 'approved_at', 'source')
    readonly_fields = ('approved_at',)
