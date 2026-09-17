from django.shortcuts import render
from .models import OrderCustomerQuerySet, Product, Order, Customer


# def list_order_customer(request):
#     list_total = Order.objects.all().select_related("customer")
#     return render(request,"list-order-customer.html",{"items":list_total})


def list_order_customer(request):
    # IMPORTANTE 
    # LA SINTAXIS : MODELO → MANAGER → MÉTODO DEL QUERYSET
    list_total = Order.objectsc.with_customer()
    return render(request,"list-order-customer.html",{"items":list_total})