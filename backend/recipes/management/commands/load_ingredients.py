import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загружает ингредиенты в базу данных"

    def handle(self, *args, **options):
        file_path = settings.BASE_DIR.parent / "data" / "ingredients.json"
        with open(file_path, encoding="utf-8") as file:
            ingredients = json.load(file)
        created_count = 0
        for ingredient in ingredients:
            _, created = Ingredient.objects.get_or_create(
                name=ingredient["name"],
                measurement_unit=ingredient["measurement_unit"],
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Загружено новых ингредиентов: {created_count}")
        )
