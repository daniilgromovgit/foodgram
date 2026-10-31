import pytest
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
)
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_favorite_and_shopping_cart_endpoints(user, recipe):
    client = APIClient()
    client.force_authenticate(user=user)

    favorite_response = client.post(f'/api/recipes/{recipe.id}/favorite/')
    assert favorite_response.status_code == 201
    assert Favorite.objects.filter(user=user, recipe=recipe).exists()

    cart_response = client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
    assert cart_response.status_code == 201
    assert ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

    remove_favorite_response = client.delete(
        f'/api/recipes/{recipe.id}/favorite/'
    )
    assert remove_favorite_response.status_code == 204

    remove_cart_response = client.delete(
        f'/api/recipes/{recipe.id}/shopping_cart/'
    )
    assert remove_cart_response.status_code == 204


@pytest.mark.django_db
def test_download_shopping_cart_sums_ingredients(user):
    client = APIClient()
    client.force_authenticate(user=user)

    ingredient = Ingredient.objects.create(name='мука', measurement_unit='г')

    recipe1 = Recipe.objects.create(
        name='Блины',
        text='Тестовый рецепт 1',
        cooking_time=10,
        author=user,
        image='recipes/blini.jpg',
    )
    recipe2 = Recipe.objects.create(
        name='Оладьи',
        text='Тестовый рецепт 2',
        cooking_time=15,
        author=user,
        image='recipes/oladji.jpg',
    )

    RecipeIngredient.objects.create(
        recipe=recipe1,
        ingredient=ingredient,
        amount=100,
    )
    RecipeIngredient.objects.create(
        recipe=recipe2,
        ingredient=ingredient,
        amount=50,
    )

    ShoppingCart.objects.create(user=user, recipe=recipe1)
    ShoppingCart.objects.create(user=user, recipe=recipe2)

    response = client.get('/api/recipes/download_shopping_cart/')
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert 'мука (г) - 150' in content


@pytest.mark.django_db
def test_subscribe_endpoints(user, user2, recipe):
    recipe.author = user2
    recipe.save(update_fields=['author'])

    client = APIClient()
    client.force_authenticate(user=user)

    subscribe_response = client.post(f'/api/users/{user2.id}/subscribe/')
    assert subscribe_response.status_code == 201
    assert Subscription.objects.filter(follower=user, following=user2).exists()

    subscriptions_response = client.get('/api/users/subscriptions/')
    assert subscriptions_response.status_code == 200
    data = subscriptions_response.json()
    assert data['count'] == 1
    assert data['results'][0]['id'] == user2.id

    unsubscribe_response = client.delete(f'/api/users/{user2.id}/subscribe/')
    assert unsubscribe_response.status_code == 204
