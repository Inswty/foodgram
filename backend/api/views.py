from io import BytesIO

from django.db.models import BooleanField, Exists, F, OuterRef, Sum, Value
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.urls import reverse
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from core.permissions import IsOwnerOrReadOnly
from core.services import generate_unique_short_code

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, Tag, ShoppingCart
)
from users.models import Subscription
from .filters import IngredientSearchFilter, RecipeFilter
from .serializers import (
    AvatarSerializer, FavoriteWriteSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, ShoppingCartWriteSerializer, ShortRecipeSerializer,
    SubscriptionSerializer, TagSerializer, IngredientSerializer, UserSerializer
)


class UserViewSet(DjoserUserViewSet):
    """Расширенный ViewSet для работы с пользователями"""
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=('put', 'patch', 'delete'),
            url_path='me/avatar', serializer_class=AvatarSerializer)
    def avatar(self, request):
        """
        Обновление аватара текущего пользователя
        Принимает Base64 строку в поле 'avatar'.
        """
        user = request.user
        if request.method in ('PUT', 'PATCH'):
            if 'avatar' not in request.data:
                return Response(
                    {'error': 'Поле "avatar" обязательно для заполнения.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=('get',))
    def subscriptions(self, request):
        """Получение списка подписок"""
        queryset = self.get_queryset().filter(
            author_subscribers__user=request.user
        ).prefetch_related('recipes')

        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, id=None):
        """Управление подпиской"""
        author = self.get_object()
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'error': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(user=user,
                                           author=author).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                author=author
            )
            if not subscription.exists():
                return Response(
                    {'error': 'Подписка не найдена'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('tags', 'ingredients')
    )
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Вы не авторизованы.")
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            return qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        # Для анонимов проставим False
        return qs.annotate(
            is_favorited=Value(False, output_field=BooleanField()),
            is_in_shopping_cart=Value(False, output_field=BooleanField())
        )

    def _add_item(self, serializer_class, pk):
        """Метод добавления рецепта в избранное или корзину."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user

        data = {'user': user.id, 'recipe': recipe.id}
        serializer = serializer_class(
            data=data, context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            ShortRecipeSerializer(
                recipe, context={'request': self.request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    def _delete_item(self, model, pk):
        user = self.request.user
        get_object_or_404(Recipe, pk=pk)
        deleted, _ = model.objects.filter(user=user, recipe__id=pk).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return self._add_item(FavoriteWriteSerializer, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self._delete_item(Favorite, pk)

    @action(detail=True, methods=['post'], permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        return self._add_item(ShoppingCartWriteSerializer, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self._delete_item(ShoppingCart, pk)

    @staticmethod
    def _format_shopping_cart(ingredients):
        """Формирование строки с содержимым корзины."""
        text_content = 'Foodgram - Список покупок\n' + '=' * 30 + '\n\n'
        text_content += '\n'.join(
            f'{i}. {item["name"]} — {item["total_amount"]}'
            f' {item["measurement_unit"]}'
            for i, item in enumerate(ingredients, start=1)
        )
        return text_content

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Скачать список покупок в виде текстового файла."""
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        if not ingredients:
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )
        text_content = self._format_shopping_cart(ingredients)
        file_obj = BytesIO(text_content.encode('utf-8'))
        response = FileResponse(file_obj, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(detail=True, url_path='get-link', methods=['get'])
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        generate_unique_short_code(recipe)
        short_url = request.build_absolute_uri(
            reverse('recipe_short_link', args=[recipe.short_code])
        )
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
