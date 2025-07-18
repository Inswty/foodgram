from django.db import models
from django.contrib.auth.models import AbstractUser


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
