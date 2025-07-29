from django.db.models import Case, When, Value, IntegerField
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorited_by__user=user)
        if value:
            return Recipe.objects.none()
        return queryset

    def filter_is_in_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(added_to_carts__user=user)
        if value:
            return Recipe.objects.none()
        return queryset


class IngredientSearchFilter(SearchFilter):
    """
    Поиск по частичному вхождению в начале названия и в произвольном месте
    с приоритетной сортировкой.
    """
    search_param = 'name'

    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '')
        return [params] if params else []

    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        if not search_terms:
            return queryset.order_by('name')
        search_term = search_terms[0]
        return queryset.filter(
            name__icontains=search_term
        ).annotate(
            match_priority=Case(
                When(name__istartswith=search_term, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-match_priority', 'name')
