from django.template import Context, Engine
from django.utils import timezone

SHOPPING_LIST_TEMPLATE_TEXT = """
Список покупок
Дата составления: {{ generated_at }}

Продукты:
{% for ingredient in ingredients %}
{{ forloop.counter }}. {{ ingredient.name }} ({{ ingredient.measurement_unit }}) - {{ ingredient.total_amount }}
{% empty %}
Нет продуктов.
{% endfor %}

Рецепты:
{% for recipe in recipes %}
{{ forloop.counter }}. {{ recipe.name }} - {{ recipe.author }}
{% if recipe.tags %} ({{ recipe.tags|join:", " }}){% endif %}
{% empty %}
Нет рецептов.
{% endfor %}
"""

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
