from django.shortcuts import render
from .models import Store

def list_store_region_product(request):
    list_store = Store.objects.with_region().with_product()
    return render(request,"list-store-region-product.html",{"items":list_store})
