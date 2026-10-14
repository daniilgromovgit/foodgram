from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField(unique=True)
    slug = models.SlugField(unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(max_length=64)


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes"
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    ingredients = models.ManyToManyField(Ingredient, through="RecipeIngredient")
    image = models.ImageField(upload_to="recipes/images/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gte=1), name="positive_amount"
            ),
        ]


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_%(class)s_user_recipe",
            )
        ]


class Favorite(UserRecipeRelation):
    pass


class ShoppingCart(UserRecipeRelation):
    pass
