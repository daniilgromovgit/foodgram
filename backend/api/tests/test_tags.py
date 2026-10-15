import pytest
from recipes.models import Tag
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_get_tags():
    tag = Tag.objects.create(name='Завтрак', slug='breakfast')
    client = APIClient()
    response = client.get('/api/tags/')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['id'] == tag.id
    assert data[0]['name'] == 'Завтрак'
    assert data[0]['slug'] == 'breakfast'


@pytest.mark.django_db
def test_get_tag():
    tag = Tag.objects.create(
        name='Завтрак',
        slug='breakfast',
    )
    client = APIClient()
    response = client.get(f'/api/tags/{tag.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == tag.id
    assert data['name'] == tag.name
    assert data['slug'] == tag.slug


@pytest.mark.django_db
def test_create_tag_not_allowed():
    client = APIClient()

    response = client.post(
        '/api/tags/',
        {
            'name': 'Обед',
            'slug': 'lunch',
        },
        format='json',
    )
    assert Tag.objects.count() == 0
    assert response.status_code == 405
