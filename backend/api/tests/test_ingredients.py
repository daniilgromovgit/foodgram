import pytest
from recipes.models import Ingredient
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_get_ingredients():
    ingredient = Ingredient.objects.create(name='сахар', measurement_unit='г')
    client = APIClient()
    response = client.get('/api/ingredients/')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['id'] == ingredient.id
    assert data[0]['name'] == ingredient.name
    assert data[0]['measurement_unit'] == ingredient.measurement_unit


@pytest.mark.django_db
def test_get_ingredient():
    ingredient = Ingredient.objects.create(name='сахар', measurement_unit='г')
    client = APIClient()
    response = client.get(f'/api/ingredients/{ingredient.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == ingredient.id
    assert data['name'] == ingredient.name
    assert data['measurement_unit'] == ingredient.measurement_unit


@pytest.mark.django_db
def test_search_ingredietns_by_name():
    Ingredient.objects.create(name='сахар', measurement_unit='г')
    Ingredient.objects.create(name='салат', measurement_unit='г')
    Ingredient.objects.create(name='масло', measurement_unit='г')
    client = APIClient()
    response = client.get('/api/ingredients/?name=са')
    assert response.status_code == 200
    data = response.json()
    names = [ingredient['name'] for ingredient in data]
    assert 'сахар' in names
    assert 'салат' in names
    assert 'масло' not in names


@pytest.mark.django_db
def test_create_ingredient_not_allowed():
    client = APIClient()

    response = client.post(
        '/api/ingredients/',
        {
            'name': 'мука',
            'measurement_unit': 'г',
        },
        format='json',
    )

    assert response.status_code == 405
    assert Ingredient.objects.count() == 0
