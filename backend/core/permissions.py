from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ на чтение всем,
    на изменение — только владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить безопасные методы (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Только владелец объекта может редактировать его
        return obj.author == request.user
