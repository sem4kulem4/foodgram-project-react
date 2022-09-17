from django.db import models
from django.urls import reverse

from users.models import User


class Tag(models.Model):
    name = models.CharField(blank=False, max_length=200, unique=True)
    color = models.CharField(blank=False, unique=True, max_length=7)
    slug = models.SlugField(blank=False, max_length=200, unique=True)

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.name} - {self.color}'


class Ingredient(models.Model):
    name = models.CharField(blank=False, max_length=200)
    measurement_unit = models.CharField(blank=False, max_length=50)

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(max_length=200, blank=False)
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
        blank=False
    )
    text = models.TextField(
        blank=False,
        max_length=500,
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(Ingredient, through='IngredientsInRecipe')
    tags = models.ManyToManyField(Tag, through='TagsInRecipe')
    cooking_time = models.IntegerField(
        blank=False,
        verbose_name='Время приготовления в минутах',
    )

    def __str__(self):
        return f'{self.name} by {self.author}'


class IngredientsInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт, к котором присутствует этот ингридиент'
    )
    amount = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество ингридиента в данном рецепте'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='single_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class TagsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тэг,  которому соответствует данный рецепт'
    )

    def __str__(self):
        return f'{self.tag} in {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь, который добавляет рецепт в избранное'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт, который добавлен в избранное'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_user',
        verbose_name='Пользователь, который добавляет рецепт в список покупок'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipe',
        verbose_name='Рецепт, который добавлен в список покупок'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppingcart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в список покупок {self.recipe}'
