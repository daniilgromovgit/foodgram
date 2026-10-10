import pytest
from django.db import IntegrityError

from recipes.models import Tag


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
