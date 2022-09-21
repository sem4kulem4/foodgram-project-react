from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from users.models import User, Follow
from recipes.models import ShoppingCart
from .models import Favorite, Ingredient, IngredientsInRecipe, Recipe, Tag


class CopyExistingUserSerializer(serializers.ModelSerializer):
    """Для существующих пользователей."""

    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        user = self.context.get('request').user
        return Follow.objects.filter(user=user, author=obj).exists()


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

    def validate(self, data):
        amount = data.get('amount')
        if amount < 0:
            raise serializers.ValidationError(
                f'Количество ингредиента не может быть отрицательным!'
            )
        return data


class TagsInRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    author = CopyExistingUserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientAmountSerializer(
        many=True,
        source='ingredientsinrecipe_set',
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_in_shopping_cart'
        )

    def get_is_in_shopping_cart(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField()
    tags = serializers.ListSerializer(child=serializers.IntegerField())
    ingredients = RecipeIngredientAmountSerializer(
        many=True,
        source='ingredientsinrecipe_set'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        cooking_time = data.get('cooking_time')
        ingredients_list = data.get('ingredientsinrecipe_set')
        no_double_ingredients_id = []

        for ingredient in ingredients_list:
            ingredient_id = ingredient.get('ingredient').get('id')
            if ingredient_id in no_double_ingredients_id:
                raise serializers.ValidationError(
                    'В запросе замечены дублирующиеся ингредиенты!'
                )
            else:
                no_double_ingredients_id.append(ingredient.get('ingredient').get('id'))

        if len(ingredients_list) == 0:
            return serializers.ValidationError('Вы не добавили ни одного ингредиента!')
        if cooking_time < 0:
            raise serializers.ValidationError('Время приготовления не может быть отрицательным!')
        return data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Короткий вариант рецепта для отображения в подписках."""
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Favorite
        fields = ('id',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id',)
        read_only_fields = ('name', 'image', 'cooking_time')
