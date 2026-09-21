from django.contrib import admin
from django.urls import path
from .import views
 
urlpatterns = [
    path('', views.list_article_author, name = "index"),
    path('labels/',views.list_article_label, name = "index")
]