from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AvatarView, IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
urlpatterns = router.urls
urlpatterns += [
    path('users/me/avatar/', AvatarView.as_view(), name='user-avatar'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
