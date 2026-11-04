from django.template import Context, Engine
from django.utils import timezone

SHOPPING_LIST_TEMPLATE_TEXT = (
    'Список покупок\n'
    'Дата составления: {{ generated_at }}\n\n'
    'Продукты:\n'
    '{% for ingredient in ingredients %}\n'
    '{{ forloop.counter }}. {{ ingredient.name }} '
    '({{ ingredient.measurement_unit }}) - '
    '{{ ingredient.total_amount }}\n'
    '{% empty %}\n'
    'Нет продуктов.\n'
    '{% endfor %}\n\n'
    'Рецепты:\n'
    '{% for recipe in recipes %}\n'
    '{{ forloop.counter }}. {{ recipe.name }} - {{ recipe.author }}\n'
    '{% if recipe.tags %} ({{ recipe.tags|join:", " }}){% endif %}\n'
    '{% empty %}\n'
    'Нет рецептов.\n'
    '{% endfor %}\n'
)

SHOPPING_LIST_TEMPLATE = Engine().from_string(SHOPPING_LIST_TEMPLATE_TEXT)


def build_shopping_list_content(ingredients, recipes):
    return SHOPPING_LIST_TEMPLATE.render(
        Context(
            {
                'generated_at': timezone.localtime().strftime(
                    '%d.%m.%Y %H:%M'
                ),
                'ingredients': ingredients,
                'recipes': recipes,
            }
        )
    )
