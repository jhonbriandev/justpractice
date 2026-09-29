from django.urls import path
from .import views
 

urlpatterns = [
    path("",views.list_order_customer_product, name="index"),
]