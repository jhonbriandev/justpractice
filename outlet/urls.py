from django.urls import path
from .import views
 
urlpatterns = [
    path('', views.list_store_region_product, name = "index"),
     
]