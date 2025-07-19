from rest_framework import viewsets

from .serializers import RecipeSerializer
from .models import Ingredient, Recipe, Tag


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe
    serializer_class = RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient


class DownloadShoppingCartView(viewsets.ModelViewSet):
    pass
