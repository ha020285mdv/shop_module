from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit.
    Retrieve - all users
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_superuser
        return True


class IsAdminOrCreateOnly(IsAdminOrReadOnly):
    """
    Custom permission to only allow admins to edit.
    All authenticated users can retrieve and create.
    Make sure you use filter_backends to allow users retrieve only their own objects
    """
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_authenticated
        if request.method == 'POST':
            return request.user.is_authenticated
        return request.user.is_superuser


class IsAdminOrCreateOnlyForUsers(IsAdminOrCreateOnly):
    """
    Custom permission to only allow admins to edit.
    Retrieve - all users
    Make sure you use filter_backends to allow users retrieve only their own objects
    """
    def has_permission(self, request, view):
        return request.user.is_superuser or request.method in permissions.SAFE_METHODS
