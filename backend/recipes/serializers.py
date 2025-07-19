from rest_framework import serializers

from .models import Ingredient, Recipe, Tag


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'author', 'name', 'image', 'description', 'tags', 'cooking_time'
        )


class IngredientSwerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class TagSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', 'slug')
