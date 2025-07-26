from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet, RecipeViewSet, redirect_short_link, TagViewSet
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('s/<str:short_code>/', redirect_short_link, name='recipe-short-link'),
]
