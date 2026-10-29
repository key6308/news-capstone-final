"""Application module for the Django news project."""
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


def configure_role_group(role):
    """Configure role group for the application."""
    group, _ = Group.objects.get_or_create(name=role.title())
    permission_names = {
        User.Roles.READER: ['view_article', 'view_newsletter'],
        User.Roles.EDITOR: [
            'view_article', 'change_article', 'delete_article',
            'view_newsletter', 'change_newsletter', 'delete_newsletter',
        ],
        User.Roles.JOURNALIST: [
            'view_article', 'add_article', 'change_article', 'delete_article',
            'view_newsletter', 'add_newsletter', 'change_newsletter', 'delete_newsletter',
        ],
    }[role]
    permissions = Permission.objects.filter(
        content_type__app_label='news', codename__in=permission_names
    )
    group.permissions.set(permissions)
    return group


@receiver(post_save, sender=User)
def assign_role_group(sender, instance, **kwargs):
    """Assign role group for the application."""
    group = configure_role_group(instance.role)
    instance.groups.set([group])
