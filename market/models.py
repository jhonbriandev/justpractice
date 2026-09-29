from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class OrderQuerySet(models.QuerySet):
    def with_customer(self):
        return self.select_related("customer")  
    
    def with_product(self):
        return self.prefetch_related("products")
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField('Product')
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Numero de Orden : {self.id}"
    
    objects = OrderQuerySet.as_manager()
    
    # Metodo para calcular el total de los productos
    # Usaremos sum, ademas de una expresion generadora
    # Buscamos el precio de cada producto en la lista de todos los productos
    def total_products(self):
        return sum(product.price for product in self.products.all())
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name