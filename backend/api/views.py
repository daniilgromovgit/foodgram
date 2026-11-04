from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from recipes.shopping_list import build_shopping_list_content
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from .filters import IngredientNameSearchFilter, RecipeFilterBackend
from .pagination import FoodgramPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortReadSerializer,
    RecipeWriteSerializer,
    SubscribedAuthorSerializer,
    TagSerializer,
)

User = get_user_model()


class CompatibleFileResponse(FileResponse):
    @property
    def content(self):
        return getattr(self, '_content', b'')

    @content.setter
    def content(self, value):
        self._content = value


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientNameSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )
    pagination_class = FoodgramPagination
    filter_backends = (RecipeFilterBackend,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_to_relation(self, model):
        recipe = self.get_object()
        _, created = model.objects.get_or_create(
            user=self.request.user,
            recipe=recipe,
        )
        if not created:
            relation_name = model._meta.verbose_name
            raise ValidationError(
                {
                    'errors': (
                        f'Рецепт "{recipe.name}" уже добавлен '
                        f'в {relation_name}.'
                    )
                }
            )
        return Response(
            RecipeShortReadSerializer(
                recipe,
                context={'request': self.request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def _remove_from_relation(self, pk, model):
        get_object_or_404(
            model,
            user=self.request.user,
            recipe_id=pk,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_relation(Favorite)
        return self._remove_from_relation(pk, Favorite)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_relation(ShoppingCart)
        return self._remove_from_relation(pk, ShoppingCart)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcarts__user=request.user
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        recipes = (
            Recipe.objects.filter(shoppingcarts__user=request.user)
            .select_related('author')
            .prefetch_related('tags')
            .order_by('name')
            .distinct()
        )

        content = build_shopping_list_content(
            ingredients=[
                {
                    'name': item['ingredient__name'],
                    'measurement_unit': item['ingredient__measurement_unit'],
                    'total_amount': item['total_amount'],
                }
                for item in ingredients
            ],
            recipes=[
                {
                    'name': recipe.name,
                    'author': recipe.author.username,
                    'tags': [tag.name for tag in recipe.tags.all()],
                }
                for recipe in recipes
            ],
        )
        response = CompatibleFileResponse(
            ContentFile(content.encode('utf-8')),
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain',
        )
        response.content = content.encode('utf-8')
        return response

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        return Response(
            {
                'short-link': request.build_absolute_uri(
                    reverse('recipe-short-link', args=[pk])
                )
            }
        )


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = FoodgramPagination

    @action(
        detail=False,
        methods=('put', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.user.avatar:
            request.user.avatar.delete(save=False)
            request.user.avatar = None
            request.user.save(update_fields=['avatar'])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(
            following_subscriptions__follower=request.user
        ).order_by('id')
        page = self.paginate_queryset(queryset)
        serializer = SubscribedAuthorSerializer(
            page if page is not None else queryset,
            many=True,
            context={'request': request},
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        if request.method != 'POST':
            get_object_or_404(
                Subscription,
                follower=request.user,
                following_id=id,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        author = self.get_object()
        if request.user == author:
            raise ValidationError(
                {'errors': 'Нельзя подписаться на самого себя.'}
            )

        _, created = Subscription.objects.get_or_create(
            follower=request.user,
            following=author,
        )
        if not created:
            raise ValidationError(
                {
                    'errors': (
                        f'Подписка на пользователя '
                        f'"{author.username}" уже существует.'
                    )
                }
            )

        return Response(
            SubscribedAuthorSerializer(
                author,
                context={'request': request},
            ).data,
            status=status.HTTP_201_CREATED,
        )
