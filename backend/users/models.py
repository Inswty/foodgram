from django.db import models
from django.contrib.auth.models import AbstractUser

from core.constants import MAX_STR_LENGTH


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(
        upload_to='users',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'  # Аутентификация по email
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email[:MAX_STR_LENGTH]


class Subscription(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',  # Доступ через user.subscriptions.all()
        verbose_name='Подписчик'
    )
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',  # Доступ через user.subscribers.all()
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        # Ограничения:
        constraints = [
            # Запрещаем повторные подписки
            models.UniqueConstraint(
                fields=['user', 'subscribed_to'],
                name='unique_subscription'
            ),
            # Запрещаем подписки на самого себя
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscribed_to')),
                name='no_self_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан → {self.subscribed_to}'
