from rest_framework.routers import DefaultRouter

from .views import TagViewSet

router = DefaultRouter()
router.register('tags', TagViewSet)

urlpatterns = router.urls
