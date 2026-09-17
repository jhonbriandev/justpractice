from django.contrib import admin
from .models import Author, Article, Label

admin.site.register(Author)
admin.site.register(Article)
admin.site.register(Label)
