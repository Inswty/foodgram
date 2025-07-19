from django.db import models
from django.contrib.auth.models import AbstractUser


MAX_STR_LENGTH = 20                                                 # приложение?


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(unique=True)
    avatar = models.ImageField(
        upload_to='users',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'  # Аутентификация по email
    REQUIRED_FIELDS = ('username',)  # Оставляем поле обязательным

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions',
        verbose_name='Подписчик'
    )
    subscribed_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers',
        verbose_name='Подписка'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'subscribed_to'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F('subscribed_to')),
            ),
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.subscribed_to}'[:MAX_STR_LENGTH]
