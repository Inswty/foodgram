from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag
)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1
    autocomplete_fields = ('ingredient',)
    readonly_fields = ('ingredient_measurement_unit',)

    # возвращаем measurement_unit из связанного объекта Ingredient
    def ingredient_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit
    ingredient_measurement_unit.short_description = 'Единица измерения'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author_username',
        'author_email',
        'favorites_count',
        'image_preview',
    )
    list_filter = ('tags',)
    search_fields = ('author__username', 'author__email', 'name',)
    ordering = ('name',)
    inlines = (IngredientInRecipeInline,)
    filter_horizontal = ('tags',)
    readonly_fields = ('favorites_count',)

    def author_username(self, obj):
        return obj.author.username
    author_username.short_description = 'Автор'

    def author_email(self, obj):
        return obj.author.email
    author_email.short_description = 'Email'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50">', obj.image.url
            )
        return "Нет изображения"
    image_preview.short_description = 'Изображение'

    def favorites_count(self, obj):
        # Подсчитываем количество добавлений в избранное
        return Favorite.objects.filter(recipe=obj).count()
    favorites_count.short_description = 'В избранном'


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
