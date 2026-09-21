from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# QuerySet para consultas de Order relacionadas con Customer.
class OrderCustomerQuerySet(models.QuerySet):

    def with_customer(self):
        # Encapsulamos select_related() para reutilizar esta consulta.
        # Permite obtener los datos de Customer mediante un JOIN,
        # manteniendo el resultado como un QuerySet de Order.
        # self representa el QuerySet actual obtenido desde el Manager (objects). EJ: objects.all()
        return self.select_related("customer")


# QuerySet para consultas de Order relacionadas con Product.
class OrderProductQuerySet(models.QuerySet):

    def with_products(self):
        # Encapsulamos prefetch_related() para reutilizar esta consulta.
        return self.prefetch_related("products")


class Order(models.Model):
    # Related name en plural
    
    
    # Campo FK: singular porque cada Order pertenece a un Customer.
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )
    # Campo M2M: plural porque un Order puede tener varios Product y su relacion empieza en Mayuscula
    products = models.ManyToManyField("Product")
    total = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    def __str__(self):
        return f"Numero de Orden #{self.id}"

    # Managers personalizados basados en los QuerySets anteriores.
    objectsc = OrderCustomerQuerySet.as_manager()
    objectsp = OrderProductQuerySet.as_manager()


class Product(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name