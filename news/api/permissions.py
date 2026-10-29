"""Role-based permission classes for the REST API."""

from rest_framework.permissions import BasePermission


class IsJournalist(BasePermission):
    """Define the IsJournalist class."""
    message = 'Only journalists can create articles.'

    def has_permission(self, request, view):
        """Has permission for the application."""
        return bool(request.user.is_authenticated and request.user.is_journalist)


class IsEditorOrJournalist(BasePermission):
    """Define the IsEditorOrJournalist class."""
    message = 'Only editors or journalists can modify articles.'

    def has_permission(self, request, view):
        """Has permission for the application."""
        return bool(
            request.user.is_authenticated
            and (request.user.is_editor or request.user.is_journalist)
        )


class IsReader(BasePermission):
    """Define the IsReader class."""
    message = 'Only readers can access subscribed content.'

    def has_permission(self, request, view):
        """Has permission for the application."""
        return bool(request.user.is_authenticated and request.user.is_reader)


class IsEditor(BasePermission):
    """Define the IsEditor class."""
    message = 'Only editors can use this endpoint.'

    def has_permission(self, request, view):
        """Has permission for the application."""
        return bool(request.user.is_authenticated and request.user.is_editor)
