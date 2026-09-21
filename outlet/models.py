from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class StoreQuerySet(models.QuerySet):
    def with_region(self):
        return self.select_related("region")  
    def with_product(self):
        return self.prefetch_related("products") 
    
class Store(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    products = models.ManyToManyField('ProductStore')

    def __str__(self):
        return self.name
    
    objects = StoreQuerySet.as_manager()
    
class ProductStore(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name