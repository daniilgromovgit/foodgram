import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)


@pytest.mark.django_db
def test_tag_creation():
    tag = Tag.objects.create(name='Завтрак', slug='breakfast')
    assert tag.name == 'Завтрак'
    assert tag.slug == 'breakfast'


@pytest.mark.django_db
def test_tag_slug_unique():
    Tag.objects.create(name='Завтрак', slug='breakfast')
    with pytest.raises(IntegrityError):
        Tag.objects.create(name='Ужин', slug='breakfast')


@pytest.mark.django_db
def test_tag_name_unique():
    Tag.objects.create(name='Завтрак', slug='breakfast')
    with pytest.raises(IntegrityError):
        Tag.objects.create(name='Завтрак', slug='dinner')


@pytest.mark.django_db
def test_ingredient_creation():
    ingredient = Ingredient.objects.create(name='сахар', measurement_unit='г')
    assert ingredient.name == 'сахар'
    assert ingredient.measurement_unit == 'г'


@pytest.mark.django_db
def test_recipe_creation(user, recipe):
    assert recipe.name == 'Сырники'
    assert recipe.text == 'Невероятно нежные и вкусные сырники'
    assert recipe.cooking_time == 40
    assert recipe.author == user


@pytest.mark.django_db
def test_recipe_author_relationship(user, recipe):
    assert recipe.author == user
    assert recipe in user.recipes.all()


@pytest.mark.django_db
def test_recipe_tag_relationship(recipe):
    first_tag = Tag.objects.create(name='Завтрак', slug='breakfast')
    second_tag = Tag.objects.create(
        name='Второй завтрак', slug='second-breakfast'
    )
    recipe.tags.add(first_tag, second_tag)
    assert first_tag in recipe.tags.all()
    assert second_tag in recipe.tags.all()


@pytest.mark.django_db
def test_recipe_ingredient_relationship(recipe):
    ingredient = Ingredient.objects.create(name='сахар', measurement_unit='г')
    recipe_ingredient = RecipeIngredient.objects.create(
        recipe=recipe, ingredient=ingredient, amount=100
    )
    assert ingredient in recipe.ingredients.all()
    assert recipe_ingredient.recipe == recipe
    assert recipe_ingredient.amount == 100
    assert recipe_ingredient.ingredient == ingredient


@pytest.mark.django_db
def test_unique_recipe_ingredient(recipe):
    ingredient = Ingredient.objects.create(name='сахар', measurement_unit='г')
    RecipeIngredient.objects.create(
        recipe=recipe, ingredient=ingredient, amount=100
    )
    with pytest.raises(IntegrityError):
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient, amount=101
        )


@pytest.mark.django_db
def test_recipe_ingredient_amount_positive(recipe):
    ingredient = Ingredient.objects.create(name='сахар', measurement_unit='г')
    with pytest.raises(IntegrityError):
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient, amount=0
        )


@pytest.mark.django_db
def test_recipe_image_field(recipe):
    assert recipe.image.name == 'recipes/syrniki.jpg'


@pytest.mark.django_db
def test_recipes_ordered_by_creation_date(user):
    syrniki = Recipe.objects.create(
        name='Сырники',
        text='Невероятно нежные и вкусные сырники',
        cooking_time=40,
        author=user,
        image='recipes/syrniki.jpg',
    )
    blinchiki = Recipe.objects.create(
        name='Блинчики',
        text='Невероятно нежные и вкусные блинчики',
        cooking_time=25,
        author=user,
        image='recipes/blinchiki.jpg',
    )
    recipes = Recipe.objects.all()
    assert recipes[0] == blinchiki
    assert recipes[1] == syrniki


@pytest.mark.django_db
def test_favorite_creation(user, recipe):
    favorite = Favorite.objects.create(
        user=user,
        recipe=recipe,
    )
    assert favorite.user == user
    assert favorite.recipe == recipe


@pytest.mark.django_db
def test_favorite_unique_user_recipe(user, recipe):
    Favorite.objects.create(
        user=user,
        recipe=recipe,
    )
    with pytest.raises(IntegrityError):
        Favorite.objects.create(
            user=user,
            recipe=recipe,
        )


@pytest.mark.django_db
def test_shopping_cart_creation(user, recipe):
    shopping_cart = ShoppingCart.objects.create(
        user=user,
        recipe=recipe,
    )
    assert shopping_cart.user == user
    assert shopping_cart.recipe == recipe


@pytest.mark.django_db
def test_subscription_creation(user, user2):
    subscription = Subscription.objects.create(
        follower=user2,
        following=user,
    )
    assert subscription.follower == user2
    assert subscription.following == user


@pytest.mark.django_db
def test_subscription_unique_follower_following(user, user2):
    Subscription.objects.create(
        follower=user2,
        following=user,
    )
    with pytest.raises(IntegrityError):
        Subscription.objects.create(
            follower=user2,
            following=user,
        )


@pytest.mark.django_db
def test_user_cannot_subscribe_to_self(user):
    with pytest.raises(IntegrityError):
        Subscription.objects.create(
            follower=user,
            following=user,
        )


@pytest.mark.django_db
def test_tag_name_max_length():
    tag = Tag(
        name='3' * 33,
        slug='test',
    )

    with pytest.raises(ValidationError):
        tag.full_clean()


@pytest.mark.django_db
def test_tag_slug_max_length():
    tag = Tag(
        name='test',
        slug='3' * 33,
    )

    with pytest.raises(ValidationError):
        tag.full_clean()
