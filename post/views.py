from django.shortcuts import render
from .models import Article, Author, Label

def list_article_author(request):
    list_articles = Article.objects_author.with_author()
    return render (request,"list-article-author.html",{"items":list_articles})

def list_article_label(request):
    list_labels = Article.objects_label.with_label()
    return render (request,"list-article-label.html",{"items":list_labels})