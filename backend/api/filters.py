from rest_framework.filters import BaseFilterBackend, SearchFilter


class IngredientNameSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        author = request.query_params.get('author')
        tags = request.query_params.getlist('tags')
        is_favorited = request.query_params.get('is_favorited')
        is_in_shopping_cart = request.query_params.get('is_in_shopping_cart')

        if author:
            queryset = queryset.filter(author_id=author)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags)

        if is_favorited == '1':
            queryset = (
                queryset.filter(favorites__user=request.user)
                if request.user.is_authenticated
                else queryset.none()
            )

        if is_in_shopping_cart == '1':
            queryset = (
                queryset.filter(shoppingcarts__user=request.user)
                if request.user.is_authenticated
                else queryset.none()
            )

        return queryset.distinct()
