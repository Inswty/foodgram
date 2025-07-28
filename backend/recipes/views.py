from django.db.models import Case, F, IntegerField, Sum, Value, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsOwnerOrReadOnly
from .models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, Tag, ShoppingCart
)
from .serializers import (
    RecipeReadSerializer, RecipeWriteSerializer, ShortRecipeSerializer,
    TagSerializer, IngredientSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('tags', 'ingredients').order_by('-id')
    )
    permission_classes = (IsOwnerOrReadOnly,)

    def get_permissions(self):
        if self.action in ('create', 'favorite', 'shopping_cart'):
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        is_in_cart = (
            self.request.query_params.get('is_in_shopping_cart') == '1'
        )
        author = self.request.query_params.get('author')
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
        recipe = self.get_object()
        recipe_serializer_data = ShortRecipeSerializer(recipe).data
        if action == 'POST':
            # Проверка, есть ли рецепт уже в списке (избранное или корзина)
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Если нет, добавляем в список
            model.objects.create(user=user, recipe=recipe)
            return Response(recipe_serializer_data,
                            status=status.HTTP_201_CREATED)
        elif action == 'DELETE':
            # Проверка, есть ли рецепт в списке
            item = model.objects.filter(user=user, recipe=recipe).first()
            if not item:
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if item.user != user:
                return Response(
                    {'error': 'Вы не автор этого.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        error_msg = 'Рецепт уже в избранном.'
        return self.handle_cart_or_favorite(Favorite, request.method,
                                            error_msg)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        error_msg = 'Рецепт уже в корзине.'
        return self.handle_cart_or_favorite(ShoppingCart, request.method,
                                            error_msg)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Скачать список покупок в виде текстового файла."""
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
            f'{i}. {item["name"]} — {item["total_amount"]}'
            f' {item["measurement_unit"]}'
            for i, item in enumerate(ingredients, start=1)
        )
        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment;filename="shopping_list.txt"')
        return response

    @action(detail=True, url_path='get-link', methods=['get'])
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        recipe.generate_and_assign_short_code()
        host = request.build_absolute_uri('/')[:-1]
        short_url = f'{host}/s/{recipe.short_code}'
        return Response({'short-link': short_url})


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Поиск по частичному вхождению в
        начале названия и в произвольном месте
        """
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
