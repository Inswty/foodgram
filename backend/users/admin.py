from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from .models import User, Subscription

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'recipes_count',
        'author_subscribers_count',
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

    @admin.display(description='Аватар')
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50">', obj.avatar.url
            )
        return 'Нет фото'

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Количество подписчиков')
    def author_subscribers_count(self, obj):
        return Subscription.objects.filter(user=obj).count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    list_filter = ('user',)
    search_fields = ('user',)
    ordering = ('author',)
