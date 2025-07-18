from django.db import models

from .constants import MAX_CHAR_LENGTH, MAX_SLUG_LENGTH, MAX_STR_LENGTH
from users.models import User


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=MAX_CHAR_LENGTH)
    unit = models.CharField('Единица измерения', max_length=MAX_CHAR_LENGTH)

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'


class Tag(models.Model):
    name = models.CharField(
        'Название', unique=True, max_length=MAX_CHAR_LENGTH
    )
    slug = models.SlugField(
        'Слаг', max_length=MAX_SLUG_LENGTH, unique=True,
        help_text=(
            'Слаг для тега; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.tag


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=MAX_CHAR_LENGTH)
    image = models.ImageField('Фото', upload_to='images')
    description = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридеинт',
        help_text='Выберите из списка'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления в минутах'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follows',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
        verbose_name='Подписка'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'following',),
                                    name='unique_follow'),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_prevent_self_follow',
                check=~models.Q(user=models.F('following')),
            ),
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return self.following.username[:MAX_STR_LENGTH]
