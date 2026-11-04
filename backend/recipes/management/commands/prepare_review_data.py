import base64
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class Command(BaseCommand):
    help = (
        'Создает/обновляет администратора review и наполняет базу '
        'минимальным набором рецептов для ревью.'
    )

    ADMIN_USERNAME = 'review'
    ADMIN_EMAIL = 'review@admin.ru'
    ADMIN_PASSWORD = 'revw1admn'

    AUTHOR_USERNAME = 'review_author'
    AUTHOR_EMAIL = 'review_author@example.com'
    AUTHOR_PASSWORD = 'reviewauthor123'

    PLACEHOLDER_IMAGE_RELATIVE_PATH = 'recipes/images/review-placeholder.png'
    PLACEHOLDER_IMAGE_BASE64 = (
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4'
        '//8/AAX+Av4N70a4AAAAAElFTkSuQmCC'
    )

    TAGS = (
        ('Завтрак', 'breakfast'),
        ('Обед', 'lunch'),
        ('Ужин', 'dinner'),
        ('Десерт', 'dessert'),
        ('Напитки', 'drinks'),
        ('Салаты', 'salads'),
        ('Выпечка', 'baking'),
    )

    INGREDIENTS = (
        ('Яйцо', 'шт'),
        ('Мука', 'г'),
        ('Молоко', 'мл'),
        ('Сахар', 'г'),
        ('Соль', 'г'),
        ('Помидор', 'шт'),
        ('Куриное филе', 'г'),
        ('Рис', 'г'),
        ('Яблоко', 'шт'),
        ('Чай', 'г'),
    )

    RECIPES = (
        {
            'name': 'Омлет с томатами',
            'text': (
                'Взбейте яйца, добавьте томаты и приготовьте '
                'на сковороде.'
            ),
            'cooking_time': 12,
            'author': 'author',
            'tags': ('breakfast', 'salads'),
            'ingredients': (
                ('Яйцо', 'шт', 3),
                ('Помидор', 'шт', 1),
                ('Соль', 'г', 2),
            ),
        },
        {
            'name': 'Рис с курицей',
            'text': 'Отварите рис и обжарьте курицу до готовности.',
            'cooking_time': 35,
            'author': 'author',
            'tags': ('lunch', 'dinner'),
            'ingredients': (
                ('Рис', 'г', 120),
                ('Куриное филе', 'г', 220),
                ('Соль', 'г', 3),
            ),
        },
        {
            'name': 'Сладкие блинчики',
            'text': 'Смешайте ингредиенты и выпекайте тонкие блинчики.',
            'cooking_time': 25,
            'author': 'author',
            'tags': ('breakfast', 'dessert', 'baking'),
            'ingredients': (
                ('Мука', 'г', 180),
                ('Молоко', 'мл', 300),
                ('Сахар', 'г', 30),
                ('Яйцо', 'шт', 2),
            ),
        },
        {
            'name': 'Яблочный чай',
            'text': 'Заварите чай и добавьте ломтики яблока.',
            'cooking_time': 10,
            'author': 'author',
            'tags': ('drinks', 'dessert'),
            'ingredients': (
                ('Чай', 'г', 5),
                ('Яблоко', 'шт', 1),
                ('Сахар', 'г', 10),
            ),
        },
        {
            'name': 'Салат из томатов',
            'text': 'Нарежьте томаты, посолите и подавайте.',
            'cooking_time': 8,
            'author': 'admin',
            'tags': ('salads',),
            'ingredients': (
                ('Помидор', 'шт', 2),
                ('Соль', 'г', 2),
            ),
        },
        {
            'name': 'Молочный коктейль',
            'text': 'Смешайте молоко и яблоко в блендере.',
            'cooking_time': 6,
            'author': 'admin',
            'tags': ('drinks',),
            'ingredients': (
                ('Молоко', 'мл', 250),
                ('Яблоко', 'шт', 1),
            ),
        },
        {
            'name': 'Запеченная курица',
            'text': 'Запекайте курицу в духовке до румяной корочки.',
            'cooking_time': 55,
            'author': 'admin',
            'tags': ('dinner',),
            'ingredients': (
                ('Куриное филе', 'г', 350),
                ('Соль', 'г', 4),
            ),
        },
    )

    def _ensure_placeholder_image(self):
        media_root = Path(settings.MEDIA_ROOT)
        image_path = media_root / self.PLACEHOLDER_IMAGE_RELATIVE_PATH
        image_path.parent.mkdir(parents=True, exist_ok=True)
        if not image_path.exists():
            image_path.write_bytes(
                base64.b64decode(self.PLACEHOLDER_IMAGE_BASE64)
            )
        return self.PLACEHOLDER_IMAGE_RELATIVE_PATH

    @transaction.atomic
    def handle(self, *args, **options):
        user_model = get_user_model()
        placeholder_image = self._ensure_placeholder_image()

        admin, _ = user_model.objects.update_or_create(
            username=self.ADMIN_USERNAME,
            defaults={
                'email': self.ADMIN_EMAIL,
                'first_name': 'Review',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
        )
        admin.set_password(self.ADMIN_PASSWORD)
        admin.save(update_fields=['password'])

        author, _ = user_model.objects.update_or_create(
            username=self.AUTHOR_USERNAME,
            defaults={
                'email': self.AUTHOR_EMAIL,
                'first_name': 'Recipe',
                'last_name': 'Author',
                'is_staff': False,
                'is_superuser': False,
                'is_active': True,
            },
        )
        author.set_password(self.AUTHOR_PASSWORD)
        author.save(update_fields=['password'])

        tags = {}
        for name, slug in self.TAGS:
            tag, _ = Tag.objects.get_or_create(name=name, slug=slug)
            tags[slug] = tag

        ingredients = {}
        for name, unit in self.INGREDIENTS:
            ingredient, _ = Ingredient.objects.get_or_create(
                name=name,
                measurement_unit=unit,
            )
            ingredients[(name, unit)] = ingredient

        created_recipes = 0
        for data in self.RECIPES:
            recipe_author = author if data['author'] == 'author' else admin
            recipe, created = Recipe.objects.update_or_create(
                name=data['name'],
                author=recipe_author,
                defaults={
                    'text': data['text'],
                    'cooking_time': data['cooking_time'],
                    'image': placeholder_image,
                },
            )
            if created:
                created_recipes += 1
            elif not recipe.image:
                recipe.image = placeholder_image
                recipe.save(update_fields=['image'])

            recipe.tags.set([tags[slug] for slug in data['tags']])
            recipe.recipe_ingredients.all().delete()
            RecipeIngredient.objects.bulk_create(
                [
                    RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredients[(name, unit)],
                        amount=amount,
                    )
                    for name, unit, amount in data['ingredients']
                ]
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Готово: создан/обновлен администратор review, '
                f'добавлено новых рецептов: {created_recipes}, '
                f'всего рецептов в базе: {Recipe.objects.count()}, '
                'рецептов у '
                f'{author.username}: '
                f'{Recipe.objects.filter(author=author).count()}. '
            )
        )
