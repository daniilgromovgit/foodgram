import pytest
from recipes.models import Ingredient, RecipeIngredient
from rest_framework import serializers

from api.serializers import (
    IngredientInRecipeReadSerializer,
    RecipeWriteSerializer,
    UserSerializer,
)


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

    serializer = IngredientInRecipeReadSerializer(recipe_ingredient)
    data = serializer.data

    assert data['id'] == ingredient.id
    assert data['name'] == ingredient.name
    assert data['measurement_unit'] == ingredient.measurement_unit
    assert data['amount'] == 100


@pytest.mark.django_db
def test_recipe_write_serializer_reports_all_duplicate_ingredients():
    ingredient_1 = Ingredient.objects.create(
        name='сахар',
        measurement_unit='г',
    )
    ingredient_2 = Ingredient.objects.create(
        name='мука',
        measurement_unit='г',
    )

    serializer = RecipeWriteSerializer()
    payload = [
        {'id': ingredient_1.id, 'amount': 10},
        {'id': ingredient_1.id, 'amount': 20},
        {'id': ingredient_2.id, 'amount': 30},
        {'id': ingredient_2.id, 'amount': 40},
    ]

    with pytest.raises(serializers.ValidationError, match='1.*2'):
        serializer.validate_ingredients(payload)


@pytest.mark.django_db
def test_user_serializer_is_subscribed_false(user):
    serializer = UserSerializer(user)
    data = serializer.data

    assert data['id'] == user.id
    assert data['email'] == user.email
    assert data['username'] == user.username
    assert not data['is_subscribed']
