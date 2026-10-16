import pytest
from recipes.models import Ingredient, RecipeIngredient

from api.serializers import IngredientInRecipeSerializer, UserSerializer


@pytest.mark.django_db
def test_ingredient_in_recipe_serializer(recipe):
    ingredient = Ingredient.objects.create(
        name='сахар',
        measurement_unit='г',
    )
    recipe_ingredient = RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=100,
    )

    serializer = IngredientInRecipeSerializer(recipe_ingredient)
    data = serializer.data

    assert data['id'] == ingredient.id
    assert data['name'] == ingredient.name
    assert data['measurement_unit'] == ingredient.measurement_unit
    assert data['amount'] == 100


@pytest.mark.django_db
def test_user_serializer_is_subscribed_false(user):
    serializer = UserSerializer(user)
    data = serializer.data

    assert data['id'] == user.id
    assert data['email'] == user.email
    assert data['username'] == user.username
    assert data['is_subscribed'] is False


# ////////////
