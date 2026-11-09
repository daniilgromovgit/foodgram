from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)

User = get_user_model()
admin.site.unregister(Group)


class UserRelationFilter(admin.SimpleListFilter):
    LOOKUPS = (('yes', 'Да'), ('no', 'Нет'))
    relation_name = ''

    def lookups(self, request, model_admin):
        return self.LOOKUPS

    def queryset(self, request, users):
        value = self.value()
        if value not in ('yes', 'no'):
            return users
        users = users.filter(
            **{f'{self.relation_name}__isnull': value == 'no'}
        )
        return users if value == 'no' else users.distinct()


class UserHasRecipesFilter(UserRelationFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'
    relation_name = 'recipes'


class UserHasSubscriptionsFilter(UserRelationFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'
    relation_name = 'subscriptions'


class UserHasSubscribersFilter(UserRelationFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'
    relation_name = 'following_subscriptions'


class RecipesCountMixin:
    list_display = ('recipes_count',)

    @admin.display(description='Рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()


class CookingTimeHistogramFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_bin'

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        times = sorted(recipes.values_list('cooking_time', flat=True))
        unique_times = set(times)
        if len(unique_times) < 3:
            self.ranges = {}
            return ()

        first = times[len(times) // 3]
        second = times[len(times) * 2 // 3]
        min_time = times[0]
        max_time = times[-1]
        self.ranges = {
            'fast': (min_time, first),
            'medium': (first + 1, second),
            'long': (second + 1, max_time),
        }

        return (
            ('fast', f'быстрее {first} мин'),
            ('medium', f'быстрее {second} мин'),
            ('long', 'долго'),
        )

    def queryset(self, request, recipes):
        selected_range = self.ranges.get(self.value())
        if selected_range:
            return recipes.filter(cooking_time__range=selected_range)
        return recipes


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ('ingredient',)


@admin.register(User)
class FoodgramUserAdmin(UserAdmin, RecipesCountMixin):
    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'avatar_html',
        *RecipesCountMixin.list_display,
        'subscriptions_count',
        'subscribers_count',
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = (
        UserHasRecipesFilter,
        UserHasSubscriptionsFilter,
        UserHasSubscribersFilter,
    )
    readonly_fields = ('avatar_html',)
    fieldsets = UserAdmin.fieldsets + (
        (
            'Профиль',
            {
                'fields': (
                    'avatar',
                    'avatar_html',
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Профиль',
            {'fields': ('avatar',)},
        ),
    )

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
        *RecipesCountMixin.list_display,
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'cooking_time_display',
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
    inlines = (RecipeIngredientInline,)
    filter_horizontal = ('tags',)
    readonly_fields = ('image_html',)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'author',
                    ('cooking_time', 'tags'),
                    'text',
                    ('image', 'image_html'),
                )
            },
        ),
    )

    @admin.display(description='Время')
    def cooking_time_display(self, recipe):
        return mark_safe(f'{recipe.cooking_time}<br>мин')

    @admin.display(description='В избранном')
    def favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Продукты')
    @mark_safe
    def ingredients_html(self, recipe):
        return (
            '<br>'.join(
                (
                    f'{item.ingredient.name} '
                    f'({item.ingredient.measurement_unit}): '
                    f'{item.amount}'
                )
                for item in recipe.recipe_ingredients.select_related(
                    'ingredient'
                )
            )
            or '-'
        )

    @admin.display(description='Теги')
    @mark_safe
    def tags_list(self, recipe):
        return '<br>'.join(recipe.tags.values_list('name', flat=True))

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


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('ingredient',)


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
        *RecipesCountMixin.list_display,
    )
    search_fields = ('name', 'slug')
