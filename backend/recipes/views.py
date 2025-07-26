from django.db.models import Case, F, IntegerField, Sum, Value, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from rest_framework import views, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    RecipeReadSerializer, RecipeWriteSerializer, ShortRecipeSerializer,
    TagSerializer, IngredientSerializer
)
from .models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, Tag, ShoppingCart
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('tags', 'ingredients').order_by('-id')
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        is_in_cart = self.request.query_params.get('is_in_shopping_cart') == '1'
        author = self.request.query_params.get('author')
        # Если теги не выбраны → возвращем пустой queryset
        if self.action == 'list' and not tags and not is_in_cart:
            return Recipe.objects.none()
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if self.request.query_params.get('is_favorited') == '1':
            if not self.request.user.is_authenticated:
                return Recipe.objects.none()
            queryset = queryset.filter(favorited_by__user=self.request.user)
        if is_in_cart:
            if not self.request.user.is_authenticated:
                return Recipe.objects.none()
            queryset = queryset.filter(added_to_carts__user=self.request.user)
        if author:
            queryset = queryset.filter(author=author)
        return queryset

    def handle_cart_or_favorite(self, model, action, error_msg):
        user = self.request.user
        recipe = self.get_object()  # Получаем рецепт по pk.

        # Вызываем сериализатор один раз
        recipe_serializer_data = ShortRecipeSerializer(recipe).data

        if action == 'POST':
            # Проверка, есть ли рецепт уже в списке (избранное или корзина).
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Если нет, добавляем в список.
            model.objects.create(user=user, recipe=recipe)
            return Response(recipe_serializer_data, status=status.HTTP_201_CREATED)

        elif action == 'DELETE':
            # Проверка, есть ли рецепт в списке.
            item = model.objects.filter(user=user, recipe=recipe)
            if not item.exists():
                return Response(
                    {'error': f'{error_msg} отсутствует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.delete()  # Удаляем рецепт из списка.
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        error_msg = 'Рецепт уже в избранном.'
        return self.handle_cart_or_favorite(Favorite, request.method, error_msg)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        error_msg = 'Рецепт уже в корзине.'
        return self.handle_cart_or_favorite(ShoppingCart, request.method, error_msg)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """ Скачать список покупок в виде текстового файла."""
        ingredients = (
            IngredientInRecipe.objects
            .filter(recipe__added_to_carts__user=request.user)
            .values(
                name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit')
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        if not ingredients:
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )
        text_content = 'Foodgram - Список покупок\n' + '=' * 30 + '\n\n'
        text_content += '\n'.join(
            f'{i}. {item["name"]} — {item["total_amount"]} {item["measurement_unit"]}'
            for i, item in enumerate(ingredients, start=1)
        )
        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(detail=True, url_path='get-link', methods=['get'])
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        recipe.generate_and_assign_short_code()
        host = request.build_absolute_uri('/')[:-1]
        short_url = f'{host}/s/{recipe.short_code}'
        return Response({'short-link': short_url})


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    # Поиск по частичному вхождению в начале названия и в произвольном месте
    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name).annotate(
                match_priority=Case(
                    When(name__istartswith=name, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by('-match_priority', 'name')
        else:
            queryset = queryset.order_by('name')
        return queryset


@require_GET
def redirect_short_link(request, short_code):
    recipe = get_object_or_404(Recipe, short_code=short_code)
    from django.urls import reverse
    url = reverse('recipes-detail', kwargs={'pk': recipe.id})
    if url.endswith('/'):
        url = url[:-1]
    return redirect(url, permanent=False)
