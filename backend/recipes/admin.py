from django.contrib import admin

from .models import Favorite, Ingredient, ShoppingCart, Recipe, Tag, IngredientInRecipe


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1  # Показывать одну пустую форму по умолчанию
    autocomplete_fields = ['ingredient']  # Если много ингредиентов, удобно искать


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'text',
        'cooking_time',
        'author',
    )
    list_filter = ('author__username',)
    search_fields = ('author__username', 'name',)
    ordering = ('name',)
    inlines = [IngredientInRecipeInline]
    filter_horizontal = ('tags',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_filter = ('user',)
    search_fields = ('user', 'recipe')
    ordering = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    list_filter = ('user',)
    search_fields = ('user', 'recipe')
    ordering = ('user',)
