from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)

User = get_user_model()


class RecipesCountMixin:
    recipes_count_list_display = ('recipes_count',)

    @admin.display(description='Рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


class CookingTimeHistogramFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_bin'

    @staticmethod
    def _get_thresholds(times):
        if not times:
            return 0, 0
        times = sorted(times)
        first = times[(len(times) - 1) // 3]
        second = times[(len(times) - 1) * 2 // 3]
        if second < first:
            second = first
        return first, second

    @staticmethod
    def _count_bins(queryset, first, second):
        fast_count = queryset.filter(cooking_time__lte=first).count()
        medium_count = queryset.filter(
            cooking_time__gt=first,
            cooking_time__lte=second,
        ).count()
        long_count = queryset.filter(cooking_time__gt=second).count()
        return fast_count, medium_count, long_count

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        times = list(queryset.values_list('cooking_time', flat=True))
        first, second = self._get_thresholds(times)
        fast_count, medium_count, long_count = self._count_bins(
            queryset,
            first,
            second,
        )
        return (
            ('fast', f'быстрее {first} мин ({fast_count})'),
            ('medium', f'быстрее {second} мин ({medium_count})'),
            ('long', f'долго ({long_count})'),
        )

    def queryset(self, request, queryset):
        times = list(queryset.values_list('cooking_time', flat=True))
        first, second = self._get_thresholds(times)
        if self.value() == 'fast':
            return queryset.filter(cooking_time__lte=first)
        if self.value() == 'medium':
            return queryset.filter(
                cooking_time__gt=first,
                cooking_time__lte=second,
            )
        if self.value() == 'long':
            return queryset.filter(cooking_time__gt=second)
        return queryset


@admin.register(User)
class FoodgramUserAdmin(UserAdmin, RecipesCountMixin):
    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'avatar_html',
        'recipes_count',
        'subscriptions_count',
        'subscribers_count',
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'.strip()

    @admin.display(description='Аватар')
    def avatar_html(self, user):
        if not user.avatar:
            return '-'
        return mark_safe(
            f'<img src="{user.avatar.url}" alt="{user.username}" width="64" />'
        )

    @admin.display(description='Подписок')
    def subscriptions_count(self, user):
        return user.subscriptions.count()

    @admin.display(description='Подписчиков')
    def subscribers_count(self, user):
        return user.following_subscriptions.count()


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
        *RecipesCountMixin.recipes_count_list_display,
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'cooking_time',
        'author',
        'favorite_count',
        'ingredients_html',
        'tags_list',
        'image_html',
    )
    search_fields = (
        'name',
        'author__username',
        'tags__name',
        'ingredients__name',
    )
    list_filter = ('tags', 'author', CookingTimeHistogramFilter)

    @admin.display(description='В избранном')
    def favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Продукты')
    def ingredients_html(self, recipe):
        ingredients = recipe.recipe_ingredients.select_related('ingredient')
        content = '<br>'.join(
            (
                f'{item.ingredient.name} '
                f'({item.ingredient.measurement_unit}): '
                f'{item.amount}'
            )
            for item in ingredients
        )
        return mark_safe(content or '-')

    @admin.display(description='Теги')
    def tags_list(self, recipe):
        return mark_safe(
            '<br>'.join(recipe.tags.values_list('name', flat=True))
        )

    @admin.display(description='Картинка')
    def image_html(self, recipe):
        if not recipe.image:
            return '-'
        return mark_safe(
            f'<img src="{recipe.image.url}" alt="{recipe.name}" width="80" />'
        )


@admin.register(Favorite, ShoppingCart)
class UserRecipeRelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following')
    search_fields = ('follower__username', 'following__username')


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
        *RecipesCountMixin.recipes_count_list_display,
    )
    search_fields = ('name', 'slug')
