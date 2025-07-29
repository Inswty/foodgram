from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET

from .models import Recipe


@require_GET
def redirect_short_link(request, short_code):
    recipe = get_object_or_404(Recipe, short_code=short_code)
    return redirect(f'/recipes/{recipe.id}', permanent=True)
