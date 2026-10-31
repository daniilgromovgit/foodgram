import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
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


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False

        return Subscription.objects.filter(
            follower=request.user,
            following=obj,
        ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj,
        ).exists()


class IngredientInputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                'Такого ингридиента не существует!'
            )
        return value


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')

            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientInputSerializer(many=True, allow_empty=False)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), allow_empty=False
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

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

            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags)
            self._set_ingredients(recipe, ingredients)

        return recipe

    def _set_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        ingredient_objects = Ingredient.objects.in_bulk(ingredient_ids)
        recipe_ingredients = []
        for ingredient in ingredients:
            ingredient_obj = ingredient_objects[ingredient['id']]

            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_obj,
                    amount=ingredient['amount'],
                )
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def update(self, instance, validated_data):
        with transaction.atomic():
            ingredients = validated_data.pop('ingredients', None)
            tags = validated_data.pop('tags', None)
            instance = super().update(instance, validated_data)
            if tags is not None:
                instance.tags.set(tags)
            if ingredients is not None:
                self._set_ingredients(instance, ingredients)
        return instance

    def validate_ingredients(self, ingredients):
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )

        return ingredients

    def validate_tags(self, tags):
        tag_ids = [tag.id for tag in tags]

        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError('Теги не должны повторяться.')

        return tags

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context=self.context,
        ).data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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
        return RecipeShortSerializer(
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
