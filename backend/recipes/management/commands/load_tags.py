from recipes.models import Tag

from .base_json_fixture_command import BaseJsonFixtureCommand


class Command(BaseJsonFixtureCommand):
    help = 'Загружает теги в базу данных'
    fixture_name = 'tags.json'
    model = Tag
