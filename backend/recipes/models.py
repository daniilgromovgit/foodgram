from django.db import models


class Tag(models.Model):
    name = models.CharField(unique=True)
    slug = models.SlugField(unique=True)
