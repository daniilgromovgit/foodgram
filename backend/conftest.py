import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        username='testuser',
        password='testpassword',
        email='test@example.com',
    )


@pytest.fixture
def user2():
    return get_user_model().objects.create_user(
        username='testuser2',
        password='testpassword',
        email='test2@example.com',
    )


@pytest.fixture
def recipe(user):
    from recipes.models import Recipe

    return Recipe.objects.create(
        name='Сырники',
        text='Невероятно нежные и вкусные сырники',
        cooking_time=40,
        author=user,
        image='recipes/syrniki.jpg',
    )
