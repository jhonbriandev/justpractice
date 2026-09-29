from django.shortcuts import render
from .models import Order

def list_order_customer_product(request):
    list_order = Order.objects.with_customer().with_product().filter(is_confirmed = "True")
    return render(request,"list-order-customer-product.html",{"items":list_order})

# Resumen para responder en tu entrevista oral:
# Para el modelo: "Definí un Custom QuerySet en el modelo y lo asigné al Manager del objeto."

# Para la vista: "En la vista ejecuto una consulta ORM llamando al método de nuestro Custom QuerySet, lo cual me devuelve un QuerySet optimizado."