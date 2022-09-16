from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import Follow, User
from recipes.models import Recipe
from recipes.serializers import ShortRecipeSerializer


class CreateUserSerializer(UserCreateSerializer):
    """Для создания новых пользователей."""
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ExistingUserSerializer(serializers.ModelSerializer):
    """Для существующих пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

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
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        if len(Follow.objects.filter(author=obj, user=user)) == 0:
            return False
        return True


class IsSubscribedSerializer(serializers.ModelSerializer):
    """Дополнительный вложенный сериализатор для вывода."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'recipes', 'recipes_count', 'is_subscribed')

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author_id=obj.id)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author_id=obj.id)
        return recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if Follow.objects.get(author=obj, user=user):
            return True
        return False


class FollowOnUserSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Follow
        fields = ('id',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор GET-запросов к подпискам."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes_count = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        serializer = ShortRecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes = Recipe.objects.filter(author_id=obj.id)
        return recipes.count()

    def get_is_subscribed(self, obj):
        return obj.user.follower.filter(author=obj.author).exists()

