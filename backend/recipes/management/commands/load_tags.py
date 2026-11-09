from recipes.management.commands.base_json_fixture_command import (
    BaseJsonFixtureCommand,
)
from recipes.models import Tag


class Command(BaseJsonFixtureCommand):
    help = 'Загружает теги в базу данных'
    fixture_name = 'tags.json'
    model = Tag
