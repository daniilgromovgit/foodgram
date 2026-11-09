from recipes.management.commands.base_json_fixture_command import (
    BaseJsonFixtureCommand,
)
from recipes.models import Ingredient


class Command(BaseJsonFixtureCommand):
    help = 'Загружает ингредиенты в базу данных'
    fixture_name = 'ingredients.json'
    model = Ingredient
