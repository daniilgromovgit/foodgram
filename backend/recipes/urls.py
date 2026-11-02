from django.urls import path

from .views import RecipeShortLinkRedirectView

urlpatterns = [
    path(
        '<int:pk>/',
        RecipeShortLinkRedirectView.as_view(),
        name='recipe-short-link',
    ),
]
