from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .pagination import FoodgramPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__startswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )
    pagination_class = FoodgramPagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()

        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )

        if author:
            queryset = queryset.filter(author_id=author)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags)

        if is_favorited == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(favorites__user=self.request.user)

        if is_in_shopping_cart == '1' and self.request.user.is_authenticated:
            queryset = queryset.filter(shoppingcarts__user=self.request.user)

        return queryset.distinct()

    def _add_to_relation(self, request: Request, pk: int, model):
        recipe = get_object_or_404(Recipe, id=pk)
        _, created = model.objects.get_or_create(
            user=request.user,
            recipe=recipe,
        )
        if not created:
            return Response(
                {'errors': 'Рецепт уже добавлен.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RecipeShortSerializer(
            recipe,
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_relation(self, request: Request, pk: int, model):
        recipe = get_object_or_404(Recipe, id=pk)
        deleted, _ = model.objects.filter(
            user=request.user,
            recipe=recipe,
        ).delete()
        if not deleted:
            return Response(
                {'errors': 'Рецепт отсутствует в списке.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_relation(request, pk, Favorite)
        return self._remove_from_relation(request, pk, Favorite)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_relation(request, pk, ShoppingCart)
        return self._remove_from_relation(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = (
            Ingredient.objects.filter(recipe__shoppingcarts__user=request.user)
            .values('name', 'measurement_unit')
            .annotate(total_amount=Sum('recipeingredient__amount'))
            .order_by('name')
        )

        lines = ['Список покупок:', '']
        lines.extend(
            [
                (
                    f"{item['name']} "
                    f"({item['measurement_unit']}) - "
                    f"{item['total_amount']}"
                )
                for item in ingredients
            ]
        )
        content = '\n'.join(lines)

        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(detail=True, methods=('get',), url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        short_link = request.build_absolute_uri(f'/recipes/{recipe.id}')
        return Response({'short-link': short_link})


class AvatarView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user

        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save(update_fields=['avatar'])

        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionListView(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = FoodgramPagination

    def get(self, request):
        subscriptions = request.user.subscriptions.select_related('following')
        authors = [subscription.following for subscription in subscriptions]

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(authors, request)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit},
        )
        return paginator.get_paginated_response(serializer.data)


class SubscribeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        author = get_object_or_404(request.user.__class__, id=user_id)

        if request.user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        _, created = Subscription.objects.get_or_create(
            follower=request.user,
            following=author,
        )
        if not created:
            return Response(
                {'errors': 'Подписка уже существует.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubscriptionSerializer(
            author,
            context={
                'request': request,
                'recipes_limit': request.query_params.get('recipes_limit'),
            },
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(request.user.__class__, id=user_id)
        deleted, _ = Subscription.objects.filter(
            follower=request.user,
            following=author,
        ).delete()

        if not deleted:
            return Response(
                {'errors': 'Подписка не найдена.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
