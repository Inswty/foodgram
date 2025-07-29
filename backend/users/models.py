from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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

    USERNAME_FIELD = 'email'
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
        related_name='subscriptions',
        verbose_name='Подписчик'
    )
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            # Запрещаем повторные подписки
            models.UniqueConstraint(
                fields=['user', 'subscribed_to'],
                name='unique_subscription'
            ),
        ]

    def clean(self):
        if self.user == self.subscribed_to:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def save(self, *args, **kwargs):
        self.full_clean()  # Проверим через clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} подписан → {self.subscribed_to}'
