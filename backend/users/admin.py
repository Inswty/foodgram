from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from .models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar_preview')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('email',)
    list_filter = ('is_superuser', 'is_active')
    readonly_fields = ('avatar_preview',)

    add_fieldsets = (
        (None, {
            'fields': ('email', 'username', 'first_name', 'last_name',
                       'avatar', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'avatar', 'avatar_preview'
            ),
        }),
        ('Permissions', {'fields': ('is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50">', obj.avatar.url
            )
        return "Нет фото"
    avatar_preview.short_description = 'Аватар'
