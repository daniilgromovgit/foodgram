from ...models import Ingredient
from .base_json_fixture_command import (
    BaseJsonFixtureCommand,
)


class Command(BaseJsonFixtureCommand):
    help = 'Загружает ингредиенты в базу данных'
    fixture_name = 'ingredients.json'
    model = Ingredient
