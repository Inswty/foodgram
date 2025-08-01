from django.db import models
from django.core.validators import MinValueValidator

from core.constants import (
    MAX_CHAR_LENGTH, MAX_INGREDIENT_LENGTH, MAX_SLUG_LENGTH,
    MAX_SHORT_CODE_LENGTH, MAX_STR_LENGTH, MAX_TAG_LENGTH, MAX_UNIT_LENGTH,
    MIN_VALUE_LENGTH,
)
from users.models import User


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=MAX_INGREDIENT_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement_unit'
            ),
        )

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Tag(models.Model):
    name = models.CharField(
        'Название', unique=True, max_length=MAX_TAG_LENGTH
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
        validators=(MinValueValidator(MIN_VALUE_LENGTH),),
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
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-pub_date',)

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
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe'
            ),
        )

    def __str__(self):
        return f'{self.ingredient} — {self.amount} ({self.recipe})'


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s'
            ),
        )

    def __str__(self):
        return f'{self.user} → {self.recipe} ({self._meta.verbose_name})'


class Favorite(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные рецепты'
        default_related_name = 'favorites'


class ShoppingCart(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'покупка'
        verbose_name_plural = 'покупки'
        default_related_name = 'shopping_carts'
