import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from users.models import User
from .models import Favorite, Ingredient, Recipe, Tag, TagsInRecipe, ShoppingCart, IngredientsInRecipe
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientsSerializer, RecipeSerializer,
                          TagSerializer, ShoppingCartSerializer)
from users.permissions import AuthorOrAdminOrReadOnly, ReadOnly


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ('get',)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    http_method_names = ('get',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AuthorOrAdminOrReadOnly,]

    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return (ReadOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list',):
            return RecipeSerializer
        else:
            return CreateRecipeSerializer

    def create_ingredients_in_recipe(self, recipe, ingredients):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            IngredientsInRecipe.objects.create(
                ingredient=ingredient_id,
                recipe=recipe,
                amount=amount
            )

    def create_tags_in_recipe(self, recipe, tags):
        for tag in tags:
            tag_id = tag['id']
            TagsInRecipe.objects.create(
                recipe=recipe,
                tag=tag_id
            )

    def create(self, request, *args, **kwargs):
        serializer = CreateRecipeSerializer(
            data=self.request.data,
            context={'request': self.request}
        )

        if serializer.is_valid(raise_exception=True):
            print(serializer.validated_data)
            #recipe = Recipe.objects.create(author=self.request.user, **serializer.validated_data)
            ingredients = serializer.validated_data.pop('ingredients')
            tags = serializer.validated_data.pop('tags')
            recipe = Recipe.objects.create(**serializer.validated_data)

            self.create_ingredients_in_recipe(recipe=recipe, ingredients=ingredients)
            self.create_tags_in_recipe(recipe=recipe, tags=tags)
            serializer = RecipeSerializer(
                instance=recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['post', 'delete']

    def get_queryset(self):
        current_user = self.request.user
        queryset = Favorite.objects.filter(user=current_user)
        return queryset

    def create(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(user=self.request.user, recipe=recipe).exists():
            return Response('Рецепт уже есть в избранном!', status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=self.request.user, recipe=recipe)
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not Favorite.objects.filter(user=self.request.user, recipe=recipe).exists():
            return Response('Этот рецепт не в избранном', status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user=self.request.user, recipe=recipe).delete()
        return Response('Рецепт убран из избранного')


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['post', 'delete']

    def get_queryset(self):
        current_user = self.request.user
        queryset = ShoppingCart.objects.filter(user=current_user)
        return queryset

    def create(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(user=self.request.user, recipe=recipe).exists():
            return Response('Рецепт уже есть в списке покупок!', status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.create(user=self.request.user, recipe=recipe)
        return Response('Рецептв вашем списке покупок!', status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=False)
    def delete(self, request, **kwargs):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not ShoppingCart.objects.filter(user=self.request.user, recipe=recipe).exists():
            return Response('Этого рецепта нет вашем списке покупок', status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.filter(user=self.request.user, recipe=recipe).delete()
        return Response('Рецепт убран из вашего списка покупок')


@api_view(['GET'])
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
