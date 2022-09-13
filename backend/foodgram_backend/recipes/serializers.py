from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import Ingredient, IngredientsInRecipe, Recipe, Tag
from users.models import User, Follow


# from users.serializers import ExistingUserSerializer


class TagSerializer(serializers.ModelSerializer):
    name = serializers.SlugField(
        read_only=True,
    )

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CopyExistingUserSerializer(serializers.ModelSerializer):
    """Для существующих пользователей."""
    #is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            #'is_subscribed',
        )
        #read_only_fields = ('is_subscribed',)


    # def get_is_subscribed(self, obj):
    #     print(self., obj)
    #     if Follow.objects.get(author=obj, user=obj):
    #         return True
    #     return False

class TagsInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    author = CopyExistingUserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientAmountSerializer(many=True, source='ingredientsinrecipe_set')

    class Meta:
        model = Recipe
        fields = '__all__'


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'cooking_time')
