from django.contrib import admin
from .models import (
    Favorite,
    Ingredient,
    IngredientsInRecipe,
    Tag,
    TagsInRecipe,
    Recipe,
    ShoppingCart
)


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'name', 'tags', )
    list_display = ('author', 'name', 'is_favorite_count', )

    def is_favorite_count(self, obj):
        result = Favorite.objects.filter(recipe=obj).count()
        return result


class IngredientsAdmin(admin.ModelAdmin):
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsInRecipe)
admin.site.register(TagsInRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
