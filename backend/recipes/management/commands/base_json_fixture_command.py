import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class BaseJsonFixtureCommand(BaseCommand):
    fixture_name = ''
    model = None

    def handle(self, *args, **options):
        try:
            file_path = settings.BASE_DIR.parent / 'data' / self.fixture_name
            with open(file_path, encoding='utf-8') as file:
                items = json.load(file)

            objects_to_create = [self.model(**item) for item in items]
            records_before = self.model.objects.count()
            self.model.objects.bulk_create(
                objects_to_create,
                ignore_conflicts=True,
            )
            created_count = self.model.objects.count() - records_before

            self.stdout.write(
                self.style.SUCCESS(
                    f'Загружено новых записей из {self.fixture_name}: '
                    f'{created_count}'
                )
            )
        except Exception as error:
            raise CommandError(
                f'Ошибка загрузки фикстуры {self.fixture_name}: {error}'
            ) from error
