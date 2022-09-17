from django.urls import path, include
from rest_framework import routers

from .views import (
    FavoriteViewSet, IngredientViewSet,
    RecipeViewSet, TagViewSet,
    ShoppingCartViewSet, download_shopping_cart
)

app_name = 'recipes'

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet, basename='favorite'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartViewSet, basename='shopping_cart'
)

urlpatterns = [
    path(r'recipes/download_shopping_cart/', download_shopping_cart,
         name='download'),
    path('', include(router.urls)),

]
