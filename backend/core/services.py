import random
import string
from recipes.models import Recipe
from core.constants import LENGTH_SHORT_CODE


def generate_unique_short_code(recipe: Recipe):
    """Генерирует уникальный short_code для модели Recipe."""
    if recipe.short_code:
        return recipe
    while True:
        code = ''.join(
            random.choices(
                string.ascii_lowercase + string.digits, k=LENGTH_SHORT_CODE
            )
        )
        if not Recipe.objects.filter(short_code=code).exists():
            recipe.short_code = code
            recipe.save(update_fields=['short_code'])
            return
