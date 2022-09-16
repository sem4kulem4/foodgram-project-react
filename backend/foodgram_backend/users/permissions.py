from rest_framework import permissions


class AuthorOrAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user or request.user.is_admin:
            return True
        return False


class AuthorOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

class Admin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin
