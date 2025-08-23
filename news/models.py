from django.db import models
from kegiatan.models import Kegiatan
import os
import uuid
from django.utils.text import slugify

def article_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.title)[:50]}-{uuid.uuid4().hex[:8]}.{ext}"
    return os.path.join("articles/", filename)

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)
    kegiatan = models.ForeignKey(Kegiatan, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


