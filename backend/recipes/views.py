from django.http import HttpResponseNotFound
from django.shortcuts import redirect

from .models import Recipe


def recipe_short_link_redirect(request, pk):
    if not Recipe.objects.filter(pk=pk).exists():
        return HttpResponseNotFound()
    return redirect(f'/recipes/{pk}')
