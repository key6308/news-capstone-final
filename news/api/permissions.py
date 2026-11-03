"""Role-based permission classes for the REST API."""

from rest_framework.permissions import BasePermission


class IsJournalist(BasePermission):
    """Allow access only to signed-in journalists."""
    message = 'Only journalists can create articles.'

    def has_permission(self, request, view):
        """Return ``True`` if the requesting user may use the view."""
        return bool(
            request.user.is_authenticated and request.user.is_journalist
        )


class IsEditorOrJournalist(BasePermission):
    """Allow access only to signed-in editors or journalists."""
    message = 'Only editors or journalists can modify articles.'

    def has_permission(self, request, view):
        """Return ``True`` if the requesting user may use the view."""
        return bool(
            request.user.is_authenticated
            and (request.user.is_editor or request.user.is_journalist)
        )


class IsReader(BasePermission):
    """Allow access only to signed-in readers."""
    message = 'Only readers can access subscribed content.'

    def has_permission(self, request, view):
        """Return ``True`` if the requesting user may use the view."""
        return bool(request.user.is_authenticated and request.user.is_reader)


class IsEditor(BasePermission):
    """Allow access only to signed-in editors."""
    message = 'Only editors can use this endpoint.'

    def has_permission(self, request, view):
        """Return ``True`` if the requesting user may use the view."""
        return bool(request.user.is_authenticated and request.user.is_editor)
