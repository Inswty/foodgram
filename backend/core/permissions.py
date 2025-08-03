from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        # GET/HEAD/OPTIONS — всем, остальное только аутентифицированным
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        # Чтение всем, изменения — только автору
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
