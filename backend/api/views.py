from io import BytesIO

from django.db.models import (
    BooleanField, Count, Exists, F, OuterRef, Sum, Value
)
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.urls import reverse
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from core.services import generate_unique_short_code
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, Tag, ShoppingCart
)
from users.models import Subscription, User
from .filters import IngredientSearchFilter, RecipeFilter
from .serializers import (
    AvatarSerializer, FavoriteWriteSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, ShoppingCartWriteSerializer, ShortRecipeSerializer,
    SubscriptionReadSerializer, SubscriptionCreateSerializer, TagSerializer,
    IngredientSerializer, UserSerializer
)


class UserViewSet(DjoserUserViewSet):
    """Расширенный ViewSet для работы с пользователями."""

    serializer_class = UserSerializer

    # Без этого 401 на /api/users/me/  :/
    @action(
        detail=False,
        methods=('get', 'put', 'delete'),
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSerializer,
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(detail=False, methods=('put',),
            permission_classes=(IsAuthenticated,),
            url_path='me/avatar', serializer_class=AvatarSerializer)
    def avatar(self, request):
        """
        Обновление аватара текущего пользователя
        Принимает Base64 строку в поле 'avatar'.
        """
        if 'avatar' not in request.data:
            return Response(
                {'detail': 'Поле "avatar" обязательно.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара."""
        request.user.avatar.delete()
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,),
            serializer_class=SubscriptionReadSerializer)
    def subscriptions(self, request):
        queryset = (
            self.get_queryset()
            .filter(subscribed_by__user=request.user)
            .annotate(recipes_count=Count('recipes'))
            .prefetch_related('recipes')
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        """Управление подпиской."""
        author = self.get_object()
        user = request.user
        serializer = SubscriptionCreateSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            Subscription.objects.create(user=user, author=author)
            author = (
                User.objects
                .annotate(recipes_count=Count('recipes'))
                .prefetch_related('recipes')
                .get(pk=author.pk)
            )
            return Response(
                SubscriptionReadSerializer(
                    author, context={'request': request}
                ).data, status=status.HTTP_201_CREATED
            )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Удаление подписки."""
        deleted, _ = Subscription.objects.filter(
            user=request.user,
            author=self.get_object()
        ).delete()
        if not deleted:
            return Response(
                {'error': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = (
        Recipe.objects.select_related('author')
        .prefetch_related('tags', 'ingredients')
    )
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated('Вы не авторизованы.')
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
                    Favorite.objects.filter(user=user, recipe=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user, recipe=OuterRef('pk')
                    )
                )
            )
        # Анонимы: оба поля False
        return qs.annotate(
            is_favorited=Value(False, output_field=BooleanField()),
            is_in_shopping_cart=Value(False, output_field=BooleanField())
        )

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        if recipe.author != request.user:
            raise PermissionDenied('Вы не можете обновить этот рецепт.')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        if recipe.author != request.user:
            raise PermissionDenied(
                'У вас нет прав для удаления этого рецепта.'
            )
        return super().destroy(request, *args, **kwargs)

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

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        return self._add_item(FavoriteWriteSerializer, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self._delete_item(Favorite, pk)

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
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
