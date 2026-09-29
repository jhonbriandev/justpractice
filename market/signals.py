 # Importamos la señal que Django proporciona para detectar
# cambios en relaciones ManyToMany.
from django.db.models.signals import m2m_changed

# Importamos receiver, que nos permite registrar nuestra función
# para que Django la ejecute automáticamente cuando ocurra la señal.
from django.dispatch import receiver

# Importamos el modelo Order, que contiene la relación
# ManyToMany con Product.
from .models import Order


# @receiver conecta nuestra función con la señal m2m_changed.
#
# sender = Order.products.through indica que queremos escuchar
# los cambios realizados específicamente en la relación
# ManyToMany entre Order y Product.
#
# "through" representa la tabla intermedia que Django crea
# automáticamente para manejar esta relación.
@receiver(m2m_changed, sender=Order.products.through)
def create_order(sender, instance, action, *args, **kwargs):

    # action nos indica qué operación se realizó sobre la
    # relación ManyToMany.
    #
    # post_add    → se agregaron productos.
    # post_remove → se eliminaron productos.
    # post_clear  → se eliminaron todos los productos.
    #
    # En cualquiera de estos casos debemos recalcular el total.
    if action in ["post_add", "post_remove", "post_clear"]:

        # instance representa la Order afectada.
        #
        # total_products() calcula la suma de los precios
        # de todos los productos relacionados con esta Order.
        #
        # El resultado del cálculo se asigna al campo "total".
        instance.total = instance.total_products()

        # Guardamos la Order para que el nuevo valor de "total"
        # quede almacenado en la base de datos.
        instance.save()
 
