from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsOwnerOrReadOnly
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, Tag, ShoppingCart
)
from .filters import IngredientSearchFilter, RecipeFilter
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('name',)
