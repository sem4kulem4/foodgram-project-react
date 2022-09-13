from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Ingredient, Recipe, Tag
from .serializers import (
                          IngredientsSerializer, RecipeSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ('get',)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    http_method_names = ['get', ]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def list(self, request, *args, **kwargs):
        queryset = Recipe.objects.all()
        serializer = RecipeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = Recipe.objects.all()
        recipe = get_object_or_404(queryset, pk=kwargs['pk'])
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list',):
            return RecipeSerializer
        else:
            raise Exception('я не сделяль')

