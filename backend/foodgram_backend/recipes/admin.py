from django.contrib import admin

from .models import Favorite, Ingredient, IngredientsInRecipe, Tag, TagsInRecipe, Recipe

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(IngredientsInRecipe)
admin.site.register(TagsInRecipe)
admin.site.register(Favorite)
