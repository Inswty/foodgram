from django.contrib import admin

from .models import Follow, Ingredient, Recipe, Tag


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )
    list_filter = ('user',)
    search_fields = ('user',)
    ordering = ('following',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'description',
        'cooking_time',

    )
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
