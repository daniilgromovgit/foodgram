from django.core.management.base import BaseCommand

from recipes.models import Tag

DEFAULT_TAGS = (
    {'name': 'Завтрак', 'slug': 'breakfast'},
    {'name': 'Обед', 'slug': 'lunch'},
    {'name': 'Ужин', 'slug': 'dinner'},
)


class Command(BaseCommand):
    help = 'Загружает базовые теги в базу данных'

    def handle(self, *args, **options):
        created_count = 0
        for tag_data in DEFAULT_TAGS:
            _, created = Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults={'name': tag_data['name']},
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Загружено новых тегов: {created_count}')
        )
