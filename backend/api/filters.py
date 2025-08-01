from django.db.models import Case, When, Value, IntegerField
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()  # Применяем проверку по существующим тегам
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:  # Временно оставлено
            return queryset.filter(favorites__user=user)
        if value:
            return Recipe.objects.none()
        return queryset

    def filter_is_in_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:  # Временно оставлено
            return queryset.filter(shopping_carts__user=user)
        if value:
            return Recipe.objects.none()
        return queryset


class IngredientSearchFilter(SearchFilter):
    """
    Поиск по частичному вхождению в начале названия и в произвольном месте,
    но без приоритетной сортировки.
    """
    search_param = 'name'
