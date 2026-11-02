from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import User


@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
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

    @admin.display(description='Рецептов')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписок')
    def subscriptions_count(self, user):
        return user.subscriptions.count()

    @admin.display(description='Подписчиков')
    def subscribers_count(self, user):
        return user.following_subscriptions.count()
