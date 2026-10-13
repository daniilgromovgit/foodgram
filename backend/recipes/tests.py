import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


@pytest.mark.django_db
def test_tag_creation():
    tag = Tag.objects.create(name="Завтрак", slug="breakfast")
    assert tag.name == "Завтрак"
    assert tag.slug == "breakfast"


@pytest.mark.django_db
def test_tag_slug_unique():
    Tag.objects.create(name="Завтрак", slug="breakfast")
    with pytest.raises(IntegrityError):
        Tag.objects.create(name="Ужин", slug="breakfast")


@pytest.mark.django_db
def test_tag_name_unique():
    Tag.objects.create(name="Завтрак", slug="breakfast")
    with pytest.raises(IntegrityError):
        Tag.objects.create(name="Завтрак", slug="dinner")


@pytest.mark.django_db
def test_ingredient_creation():
    ingredient = Ingredient.objects.create(name="сахар", measurement_unit="г")
    assert ingredient.name == "сахар"
    assert ingredient.measurement_unit == "г"


@pytest.mark.django_db
def test_recipe_creation():
    user = get_user_model().objects.create_user(
        username="testuser", password="testpassword"
    )
    recipe = Recipe.objects.create(
        name="Сырники",
        text="Невероятно нежные и вкусные сырники",
        cooking_time=40,
        author=user,
    )
    assert recipe.name == "Сырники"
    assert recipe.text == "Невероятно нежные и вкусные сырники"
    assert recipe.cooking_time == 40
    assert recipe.author == user


@pytest.mark.django_db
def test_recipe_author_relationship():
    user = get_user_model().objects.create_user(
        username="testuser", password="testpassword"
    )
    recipe = Recipe.objects.create(
        name="Сырники",
        text="Невероятно нежные и вкусные сырники",
        cooking_time=40,
        author=user,
    )
    assert recipe.author == user
    assert recipe in user.recipes.all()


@pytest.mark.django_db
def test_recipe_tag_relationship():
    user = get_user_model().objects.create_user(
        username="testuser", password="testpassword"
    )
    first_tag = Tag.objects.create(name="Завтрак", slug="breakfast")
    second_tag = Tag.objects.create(name="Второй завтрак", slug="second-breakfast")
    recipe = Recipe.objects.create(
        name="Сырники",
        text="Невероятно нежные и вкусные сырники",
        cooking_time=40,
        author=user,
    )
    recipe.tags.add(first_tag, second_tag)
    assert first_tag in recipe.tags.all()
    assert second_tag in recipe.tags.all()


@pytest.mark.django_db
def test_recipe_ingredient_relationship():
    user = get_user_model().objects.create_user(
        username="testuser", password="testpassword"
    )
    ingredient = Ingredient.objects.create(name="сахар", measurement_unit="г")
    recipe = Recipe.objects.create(
        name="Сырники",
        text="Невероятно нежные и вкусные сырники",
        cooking_time=40,
        author=user,
    )
    recipe_ingredient = RecipeIngredient.objects.create(
        recipe=recipe, ingredient=ingredient, amount=100
    )
    assert ingredient in recipe.ingredients.all()
    assert recipe_ingredient.recipe == recipe
    assert recipe_ingredient.amount == 100
    assert recipe_ingredient.ingredient == ingredient


@pytest.mark.django_db
def test_unique_recipe_ingredient():
    user = get_user_model().objects.create_user(
        username="testuser", password="testpassword"
    )
    recipe = Recipe.objects.create(
        name="Сырники",
        text="Невероятно нежные и вкусные сырники",
        cooking_time=40,
        author=user,
    )
    ingredient = Ingredient.objects.create(name="сахар", measurement_unit="г")
    RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=100)
    with pytest.raises(IntegrityError):
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient, amount=101
        )


@pytest.mark.django_db
def test_recipe_ingredient_amount_positive():
    user = get_user_model().objects.create_user(
        username="testuser", password="testpassword"
    )
    recipe = Recipe.objects.create(
        name="Сырники",
        text="Невероятно нежные и вкусные сырники",
        cooking_time=40,
        author=user,
    )
    ingredient = Ingredient.objects.create(name="сахар", measurement_unit="г")
    with pytest.raises(IntegrityError):
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=0)


@pytest.mark.django_db
def test_recipe_image_field():
    user = get_user_model().objects.create_user(
        username="testuser", password="testpassword"
    )
    recipe = Recipe.objects.create(
        name="Сырники",
        text="Невероятно нежные и вкусные сырники",
        cooking_time=40,
        author=user,
        image="recipes/syrniki.jpg",
    )
    assert recipe.image.name == "recipes/syrniki.jpg"


@pytest.mark.django_db
def test_recipes_ordered_by_creation_date():
    user = get_user_model().objects.create_user(
        username="testuser", password="testpassword"
    )
    syrniki = Recipe.objects.create(
        name="Сырники",
        text="Невероятно нежные и вкусные сырники",
        cooking_time=40,
        author=user,
        image="recipes/syrniki.jpg",
    )
    blinchiki = Recipe.objects.create(
        name="Блинчики",
        text="Невероятно нежные и вкусные блинчики",
        cooking_time=25,
        author=user,
        image="recipes/blinchiki.jpg",
    )
    recipes = Recipe.objects.all()
    assert recipes[0] == blinchiki
    assert recipes[1] == syrniki
