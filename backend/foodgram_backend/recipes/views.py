import csv

import django_filters
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import status, viewsets, permissions, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import (
    Favorite, Ingredient,
    Recipe, Tag,
    TagsInRecipe, ShoppingCart,
    IngredientsInRecipe
)
from .filters import RecipeFilter
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientsSerializer, RecipeSerializer,
                          TagSerializer, ShoppingCartSerializer,
                          ShortRecipeSerializer)
from users.permissions import AuthorOrAdminOrReadOnly, ReadOnly


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ('get',)
    pagination_class = None


class IngredientSearchFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    http_method_names = ('get',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 6
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_class = RecipeFilter
    ordering_fields = ('name', 'author')

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            user = self.request.user
            queryset = Recipe.objects.all()
            is_favorited = int(
                self.request.query_params.get('is_favorited', default=0)
            )
            is_in_shopping_cart = int(
                self.request.query_params.get('is_in_shopping_cart', default=0)
            )
            author_id = int(
                self.request.query_params.get('author', default=0)
            )
            tags = self.request.query_params.getlist('tags', default=0)

            if is_favorited == 1:
                queryset = queryset.filter(favorite_recipe__user=user)
            if is_in_shopping_cart == 1:
                queryset = queryset.filter(shopping_cart_recipe__user=user)
            if author_id != 0:
                queryset = queryset.filter(author_id=author_id)
            return queryset
        return Recipe.objects.all()

    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return (ReadOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list',):
            return RecipeSerializer
        return CreateRecipeSerializer

    def create_ingredients_in_recipe(self, recipe, ingredients):
        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient']['id']
            amount = ingredient['amount']
            IngredientsInRecipe.objects.create(
                ingredient_id=ingredient_id,
                recipe=recipe,
                amount=amount
            )

    def create_tags_in_recipe(self, recipe, tags):
        for tag in tags:
            TagsInRecipe.objects.create(
                recipe=recipe,
                tag_id=tag
            )

    def update(self, request, *args, **kwargs):
        serializer = CreateRecipeSerializer(
            data=self.request.data,
            context={'request': self.request}
        )

        serializer.is_valid(raise_exception=True)
        ingredients = serializer.validated_data.pop('ingredientsinrecipe_set')
        tags = serializer.validated_data.pop('tags')
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        TagsInRecipe.objects.filter(recipe=recipe).delete()
        IngredientsInRecipe.objects.filter(recipe_id=recipe).delete()
        Recipe.objects.update(**serializer.validated_data)
        self.create_ingredients_in_recipe(
            recipe=recipe,
            ingredients=ingredients
        )
        self.create_tags_in_recipe(recipe=recipe, tags=tags)
        serializer = RecipeSerializer(
            instance=recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        serializer = CreateRecipeSerializer(
            data=self.request.data,
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        ingredients = serializer.validated_data.pop('ingredientsinrecipe_set')
        tags = serializer.validated_data.pop('tags')
        recipe = Recipe.objects.create(**serializer.validated_data)

        self.create_ingredients_in_recipe(
            recipe=recipe,
            ingredients=ingredients
        )
        self.create_tags_in_recipe(recipe=recipe, tags=tags)
        serializer = RecipeSerializer(
            instance=recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('post', 'delete')

    def get_queryset(self):
        current_user = self.request.user
        queryset = Favorite.objects.filter(user=current_user)
        return queryset

    def create(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(
                user=self.request.user, recipe=recipe
        ).exists():
            return Response(
                'Рецепт уже есть в избранном!',
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite = Favorite.objects.create(
            user=self.request.user, recipe=recipe
        )
        data = {
            'id': favorite.recipe.id,
            'name': favorite.recipe.name,
            'image': favorite.recipe.image,
            'cooking_time': favorite.recipe.cooking_time
        }
        serializer_output = ShortRecipeSerializer(recipe, data=data)

        serializer_output.is_valid(raise_exception=True)
        return Response(
            serializer_output.data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not Favorite.objects.filter(
                user=self.request.user, recipe=recipe
        ).exists():
            return Response(
                'Этот рецепт не в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.filter(user=self.request.user, recipe=recipe).delete()
        return Response('Рецепт убран из избранного')


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('post', 'delete')

    def get_queryset(self):
        current_user = self.request.user
        queryset = ShoppingCart.objects.filter(user=current_user)
        return queryset

    def create(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(
                user=self.request.user, recipe=recipe
        ).exists():
            return Response(
                'Рецепт уже есть в списке покупок!',
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=self.request.user, recipe=recipe)
        return Response(
            'Рецептв вашем списке покупок!',
            status=status.HTTP_201_CREATED
        )

    @action(methods=('delete',), detail=False)
    def delete(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not ShoppingCart.objects.filter(
                user=self.request.user, recipe=recipe
        ).exists():
            return Response(
                'Этого рецепта нет вашем списке покупок',
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.filter(
            user=self.request.user,
            recipe=recipe
        ).delete()
        return Response('Рецепт убран из вашего списка покупок')


@api_view(('GET',))
def download_shopping_cart(request):
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    ingredients = IngredientsInRecipe.objects.filter(
        recipe__author=request.user.id
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(ingredient_amount=Sum('amount')).values_list(
        'ingredient__name', 'ingredient_amount', 'ingredient__measurement_unit'
    )
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="'
                                   f'{request.user}.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    for product in list(ingredients):
        writer.writerow(product)
    return response
