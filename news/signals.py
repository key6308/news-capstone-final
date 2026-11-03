"""Signal handlers that keep each user's permission group in sync with role."""
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


def configure_role_group(role):
    """Create or update the permission group for a role.

    Args:
        role (str): A value from :class:`news.models.User.Roles`.

    Returns:
        django.contrib.auth.models.Group: The group named after the role,
        with its permissions set to match that role.
    """
    group, _ = Group.objects.get_or_create(name=role.title())
    permission_names = {
        User.Roles.READER: ['view_article', 'view_newsletter'],
        User.Roles.EDITOR: [
            'view_article', 'change_article', 'delete_article',
            'view_newsletter', 'change_newsletter', 'delete_newsletter',
        ],
        User.Roles.JOURNALIST: [
            'view_article', 'add_article', 'change_article', 'delete_article',
            'view_newsletter', 'add_newsletter', 'change_newsletter',
            'delete_newsletter',
        ],
    }[role]
    permissions = Permission.objects.filter(
        content_type__app_label='news', codename__in=permission_names
    )
    group.permissions.set(permissions)
    return group


def role_changed(instance, update_fields=None):
    """Return whether a saved user's role differs from the stored one.

    Args:
        instance (news.models.User): The user that was saved.
        update_fields (frozenset, optional): The fields passed to
            ``save(update_fields=...)``, or ``None`` for a full save.

    Returns:
        bool: ``False`` if the save could not have changed the role (for
        example the ``last_login`` update made at sign-in), otherwise whether
        the role differs from the one loaded from the database.
    """
    if update_fields is not None and 'role' not in update_fields:
        return False
    return getattr(instance, '_loaded_role', None) != instance.role


@receiver(post_save, sender=User)
def assign_role_group(sender, instance, created=False, update_fields=None,
                      **kwargs):
    """Put a user in the permission group that matches their role.

    Connected to ``post_save`` for :class:`news.models.User`. The group is
    only rebuilt when the user is created or their role changes, not on
    every save.

    Args:
        sender (type): The model class that sent the signal.
        instance (news.models.User): The user that was saved.
        created (bool): ``True`` if the user was just created.
        update_fields (frozenset, optional): Fields named in
            ``save(update_fields=...)``, or ``None``.
        **kwargs: Extra signal arguments (unused).
    """
    if not created and not role_changed(instance, update_fields):
        return
    group = configure_role_group(instance.role)
    instance.groups.set([group])
    instance._loaded_role = instance.role
