from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from core.constants import MAX_EMAIL_LENGTH, MAX_NAME_LENGTH, MAX_STR_LENGTH


class User(AbstractUser):
    """Кастомная модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH, unique=True, verbose_name='Email'
    )
    avatar = models.ImageField(
        upload_to='users',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    first_name = models.CharField(max_length=MAX_NAME_LENGTH, blank=False)
    last_name = models.CharField(max_length=MAX_NAME_LENGTH, blank=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:MAX_STR_LENGTH]


class Subscription(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_subscriptions',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_subscribers',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            # Запрещаем повторные подписки
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
        )

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def save(self, *args, **kwargs):
        self.full_clean()  # Проверим через clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} подписан → {self.author}'
