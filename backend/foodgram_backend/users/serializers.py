from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

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
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        if len(Follow.objects.filter(author=obj, user=user)) == 0:
            return False
        return True


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор GET-запросов к подпискам."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes_count = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes_count'
    )
    recipes = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes'
    )
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_is_subscribed'
    )

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


class FollowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = (
            'user',
            'author'
        )

    def validate_subscription(self, value):
        user = self.context['request'].user
        if not user == value:
            return value
        raise serializers.ValidationError(
            'Вы не можете подписаться на самого себя'
        )


class FollowOutputSerializer(serializers.Serializer):
    """Сериализатор вывода после создания подписки."""
    id = serializers.SerializerMethodField(
        method_name='get_id'
    )
    email = serializers.SerializerMethodField(
        method_name='get_email'
    )
    username = serializers.SerializerMethodField(
        method_name='get_username'
    )
    first_name = serializers.SerializerMethodField(
        method_name='get_first_name'
    )
    last_name = serializers.SerializerMethodField(
        method_name='get_last_name'
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    def get_id(self, obj):
        id = int(self.context['id'])
        return id

    def get_email(self, obj):
        email = self.context['email']
        return email

    def get_username(self, obj):
        username = self.context['username']
        return username

    def get_first_name(self, obj):
        first_name = self.context['first_name']
        return first_name

    def get_last_name(self, obj):
        last_name = self.context['last_name']
        return last_name

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        author = User.objects.get(id=self.context['id'])
        recipes = Recipe.objects.filter(author=author)
        context = {
            'recipes': recipes
        }
        serializer = ShortRecipeSerializer(recipes, many=True, context=context)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes_count = self.context['recipes_count']
        return recipes_count
