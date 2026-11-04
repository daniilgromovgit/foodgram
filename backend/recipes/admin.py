from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from users.models import User

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)


class RecipesCountMixin:
    @admin.display(description='Рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


class UserStatsAdminMixin:
    @admin.display(description='Рецептов')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписок')
    def subscriptions_count(self, user):
        return user.subscriptions.count()

    @admin.display(description='Подписчиков')
    def subscribers_count(self, user):
        return user.following_subscriptions.count()


@admin.register(User)
class FoodgramUserAdmin(UserAdmin, UserStatsAdminMixin):
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


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
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
    list_filter = ('tags', 'author', 'cooking_time')

    @admin.display(description='В избранном')
    def favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Продукты')
    def ingredients_html(self, recipe):
        ingredients = recipe.recipe_ingredients.select_related('ingredient')
        if not ingredients.exists():
            return '-'
        return mark_safe(
            '<br>'.join(
                (
                    f'{item.ingredient.name} ({item.ingredient.measurement_unit}): '
                    f'{item.amount}'
                )
                for item in ingredients
            )
        )

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


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following')
    search_fields = ('follower__username', 'following__username')


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')
