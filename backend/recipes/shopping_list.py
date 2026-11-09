from django.utils import timezone

RUSSIAN_MONTHS = (
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря',
)


def build_shopping_list_content(ingredients, recipes):
    generated_at = timezone.localtime()
    lines = [
        'Список покупок',
        (
            f'Дата составления: {generated_at.day:02d} '
            f'{RUSSIAN_MONTHS[generated_at.month - 1]} {generated_at.year}'
        ),
        '',
        'Продукты:',
    ]

    ingredient_lines = []
    for number, ingredient in enumerate(ingredients, start=1):
        name = ingredient['name']
        capitalized_name = name[:1].upper() + name[1:]
        ingredient_lines.append(
            f'{number}. {capitalized_name} '
            f"({ingredient['measurement_unit']}) - "
            f"{ingredient['total_amount']}"
        )
    lines.extend(ingredient_lines or ['Нет продуктов.'])

    lines.extend(('', 'Рецепты:'))
    recipe_lines = []
    for number, recipe in enumerate(recipes, start=1):
        recipe_line = (
            f'{number}. {recipe.name} - {recipe.author.username}'
        )
        tags = ', '.join(tag.name for tag in recipe.tags.all())
        if tags:
            recipe_line += f' ({tags})'
        recipe_lines.append(recipe_line)
    lines.extend(recipe_lines or ['Нет рецептов.'])

    return '\n'.join(lines)
