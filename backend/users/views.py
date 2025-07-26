from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Subscription
from .serializers import SubscriptionSerializer, AvatarSerializer


class UserViewSet(DjoserUserViewSet):
    """Расширенный ViewSet для работы с пользователями"""
    permission_classes = [IsAuthenticated]

    # Метод для работы с аватаром
    @action(detail=False, methods=['put', 'patch'], url_path='me/avatar', serializer_class=AvatarSerializer)
    def avatar(self, request):
        """
        Обновление аватара текущего пользователя
        Принимает Base64 строку в поле 'avatar'
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # Методы для подписок
    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Получение списка подписок"""
        queryset = self.get_queryset().filter(
            subscribers__user=request.user
        ).prefetch_related('recipes')

        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
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
            if Subscription.objects.filter(user=user, subscribed_to=author).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Subscription.objects.create(user=user, subscribed_to=author)
            serializer = SubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                subscribed_to=author
            )
            if not subscription.exists():
                return Response(
                    {'error': 'Подписка не найдена'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
