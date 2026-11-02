from collections import Counter

import djoser
from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from rest_framework import serializers

User = get_user_model()

MIN_INGREDIENT_AMOUNT = 1
MIN_COOKING_TIME = 1


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        read_only_fields = ('amount',)


class UserSerializer(djoser.serializers.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = fields = (
            *djoser.serializers.UserSerializer.Meta.fields,
            'is_subscribed',
        )
        read_only_fields = fields

    def get_is_subscribed(self, user):
        request = self.context.get('request')

        return (
            request is not None
            and request.user.is_authenticated
            and Subscription.objects.filter(
                follower=request.user,
                following=user,
            ).exists()
        )


RECIPE_FIELDS = (
    'id',
    'tags',
    'author',
    'ingredients',
    'is_favorited',
    'is_in_shopping_cart',
    'name',
    'image',
    'text',
    'cooking_time',
    'created_at',
)


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = RECIPE_FIELDS
        read_only_fields = RECIPE_FIELDS

    def _check_user_relation(self, recipe, model):
        request = self.context.get('request')
        return (
            request is not None
            and request.user.is_authenticated
            and model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).exists()
        )

    def get_is_favorited(self, recipe):
        return self._check_user_relation(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self._check_user_relation(recipe, ShoppingCart)


class IngredientInputSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientInputSerializer(many=True, allow_empty=False)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), allow_empty=False
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'name',
            'text',
            'cooking_time',
            'image',
        )

    def create(self, validated_data):
        with transaction.atomic():
            ingredients = validated_data.pop('ingredients')
            tags = validated_data.pop('tags')
            recipe = super().create(validated_data)
            recipe.tags.set(tags)
            self._set_ingredients(recipe, ingredients)
        return recipe

    def _set_ingredients(self, recipe, ingredients):
        recipe.recipe_ingredients.all().delete()
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.tags.set(validated_data.pop('tags'))
            self._set_ingredients(instance, validated_data.pop('ingredients'))
            return super().update(instance, validated_data)

    def _validate_duplicates(self, items, item_name):
        counts = Counter(items)
        for item, count in counts.items():
            if count > 1:
                raise serializers.ValidationError(
                    f'{item_name}: {item} не должны повторяться.'
                )

    def validate_ingredients(self, ingredients):
        ingredient_list = [ingredient['id'] for ingredient in ingredients]
        self._validate_duplicates(ingredient_list, 'Ингредиенты')
        return ingredients

    def validate_tags(self, tags):
        tag_ids = [tag.id for tag in tags]
        self._validate_duplicates(tag_ids, 'Теги')
        return tags

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context,
        ).data


class RecipeShortReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = self.context.get('recipes_limit')
        queryset = obj.recipes.all()
        if recipes_limit is not None:
            queryset = queryset[:recipes_limit]
        return RecipeShortReadSerializer(
            queryset,
            many=True,
            context={'request': request},
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)
