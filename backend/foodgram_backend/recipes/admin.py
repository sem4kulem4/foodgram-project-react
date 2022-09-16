from django.contrib import admin

from .models import Favorite, Ingredient, IngredientsInRecipe, Tag, TagsInRecipe, Recipe, ShoppingCart


# На странице рецепта вывести общее число добавлений этого рецепта в избранное.
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'name', 'tags')


class IngredientsAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsInRecipe)
admin.site.register(TagsInRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
