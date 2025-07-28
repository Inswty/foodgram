import random
import string

from django.db import models
from django.core.validators import MinValueValidator

from core.constants import (
    LENGTH_SHORT_CODE, MAX_CHAR_LENGTH, MAX_SLUG_LENGTH,
    MAX_SHORT_CODE_LENGTH, MAX_STR_LENGTH
)
from users.models import User


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=MAX_CHAR_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_CHAR_LENGTH
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


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
        return self.name[:MAX_STR_LENGTH]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=MAX_CHAR_LENGTH)
    image = models.ImageField('Фото', upload_to='images')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты и укажите их количество'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(1),),
        help_text='Укажите время приготовления в минутах'
    )
    short_code = models.CharField(
        max_length=MAX_SHORT_CODE_LENGTH,
        blank=True,
        null=True,
        unique=True,
        editable=False,
        verbose_name='Короткая ссылка'
    )

    def generate_and_assign_short_code(self):
        if not self.short_code:
            while True:
                code = ''.join(
                    random.choices(
                        string.ascii_lowercase + string.digits,
                        k=LENGTH_SHORT_CODE
                    )
                )
                if not Recipe.objects.filter(short_code=code).exists():
                    self.short_code = code
                    self.save(update_fields=('short_code',))
                    break

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='used_in_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(1),),
        help_text='Укажите количество этого ингредиента'
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} — {self.amount} ({self.recipe})'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} → {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='added_to_carts',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'покупка'
        verbose_name_plural = 'покупки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} → {self.recipe}'
