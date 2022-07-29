from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit.
    Retrieve - all users
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.method in permissions.SAFE_METHODS

    def has_permission(self, request, view):
        return request.user.is_superuser if request.method == 'POST' else True


class IsAdminOrCreateOnly(IsAdminOrReadOnly):
    """
    Custom permission to only allow admins to edit.
    All authenticated users can retrieve and create.
    Make sure you use filter_backends to allow users retrieve only their own objects
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated if request.method == 'POST' else True


class IsAdminOrCreateOnlyForUsers(IsAdminOrCreateOnly):
    """
    Custom permission to only allow admins to edit.
    Retrieve - all users
    Make sure you use filter_backends to allow users retrieve only their own objects
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method == 'POST'
