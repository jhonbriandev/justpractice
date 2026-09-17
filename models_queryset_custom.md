# Modelos, QuerySets y Custom QuerySets en Django

## 1. Convenciones de nombres en Django

Django no obliga estrictamente a utilizar estas convenciones, pero son prácticas habituales y ayudan a que el código sea más claro.

### Modelos

Los modelos representan entidades y normalmente se escriben en **singular + PascalCase**:

```python
class Customer(models.Model):
    ...

class Order(models.Model):
    ...

class Product(models.Model):
    ...

class Employee(models.Model):
    ...
```

Por ejemplo:

- `Customer` → cliente
- `Order` → pedido
- `Product` → producto
- `Employee` → empleado

### Campos ForeignKey

Un `ForeignKey` representa que cada instancia pertenece o apunta a una sola instancia del modelo relacionado.

Por eso normalmente el campo se escribe en **singular + minúsculas**:

```python
customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
company = models.ForeignKey(Company, on_delete=models.CASCADE)
```

La idea es:

```
Order
  │
  └── customer ──────► Customer
```

Un `Order` tiene un `customer`.

### Campos ManyToManyField

Un `ManyToManyField` representa una relación donde una instancia puede relacionarse con varias instancias.

Por eso normalmente se utiliza **plural + minúsculas**:

```python
products = models.ManyToManyField("Product")
habilities = models.ManyToManyField("Hability")
```

Por ejemplo:

```
Order
 ├── Product
 ├── Product
 └── Product
```

Un `Order` puede tener varios `products`.

## 2. ForeignKey: campo, modelo y columna

Es importante diferenciar estos tres conceptos.

```python
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
```

**`customer`**

Es el campo `ForeignKey` del modelo `Order`.

```python
order.customer
```

Devuelve un objeto `Customer`.

**`Customer`**

Es el modelo relacionado:

```python
class Customer(models.Model):
    ...
```

**`customer_id`**

En la base de datos, Django normalmente crea una columna:

```
customer_id
```

Esta almacena el identificador del `Customer` relacionado.

Conceptualmente:

Modelo Django:

```
Order
 └── customer → Customer
```

Base de datos:

```
Order
 └── customer_id → ID de Customer
```

Por tanto: `customer` es el campo `ForeignKey` en Django, mientras que `customer_id` es la columna que normalmente existe en la base de datos.

## 3. ForeignKey vs ManyToManyField

Ejemplo:

```python
class Order(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    products = models.ManyToManyField("Product")
```

Aquí:

- `customer` → `ForeignKey`
- `products` → `ManyToManyField`

### ForeignKey

```python
customer = models.ForeignKey(Customer, ...)
```

Un pedido pertenece a un cliente:

```
Order ───────► Customer
```

### ManyToManyField

```python
products = models.ManyToManyField("Product")
```

Un pedido puede tener varios productos:

```
Order ───────► Product
   │
   ├──────────► Product
   │
   └──────────► Product
```

Además, un mismo producto puede aparecer en muchos pedidos.

Django maneja esta relación mediante una tabla intermedia.

## 4. related_name

Cuando tenemos una relación, Django también permite definir cómo acceder desde el modelo relacionado.

Ejemplo:

```python
class Order(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders"
    )
```

Ahora podemos hacer:

```python
customer.orders.all()
```

Esto significa:

> Dame todos los pedidos pertenecientes a este cliente.

Por eso normalmente un `related_name` que devuelve varios objetos se escribe en plural:

```python
related_name="orders"
related_name="employees"
related_name="products"
```

La idea general es:

```
Customer
   │
   └── orders
          ├── Order
          ├── Order
          └── Order
```

## 5. QuerySet normal

Un `QuerySet` representa un conjunto de objetos de un modelo que puede ser consultado.

Ejemplo:

```python
Order.objects.all()
```

Aquí:

```
Order
  ↓
objects
  ↓
all()
  ↓
QuerySet de Order
```

También podemos hacer:

```python
Order.objects.filter(total__gt=100)
```

o:

```python
Order.objects.get(id=1)
```

Los métodos como:

```python
.all()
.filter()
.exclude()
.get()
.order_by()
```

son herramientas normales de consulta de Django.

## 6. ¿Qué es un Custom QuerySet?

Un Custom QuerySet permite crear métodos propios para encapsular consultas que utilizamos frecuentemente.

En lugar de repetir:

```python
Order.objects.select_related("customer")
```

podemos crear:

```python
class OrderCustomerQuerySet(models.QuerySet):

    def with_customer(self):
        return self.select_related("customer")
```

Ahora la lógica de la consulta queda encapsulada dentro de `with_customer()`.

## 7. ¿Dónde se coloca un Custom QuerySet?

Normalmente se define en `models.py`, como una clase independiente:

```python
class OrderCustomerQuerySet(models.QuerySet):

    def with_customer(self):
        return self.select_related("customer")
```

No es necesario colocarlo dentro de `class Order(models.Model):`.

Es una clase separada.

## 8. self dentro del Custom QuerySet

Tenemos:

```python
class OrderCustomerQuerySet(models.QuerySet):

    def with_customer(self):
        return self.select_related("customer")
```

Aquí, `self` representa el QuerySet actual sobre el que se está ejecutando el método.

No debemos hacer esto desde la vista:

```python
Order.objectsc.with_customer(self)  # ❌ Incorrecto
```

Django proporciona `self` automáticamente.

Se utiliza:

```python
Order.objectsc.with_customer()
```

## 9. select_related()

`select_related()` se utiliza principalmente con:

- `ForeignKey`
- `OneToOneField`

Ejemplo:

```python
class OrderCustomerQuerySet(models.QuerySet):

    def with_customer(self):
        return self.select_related("customer")
```

Como `customer` es un `ForeignKey`, utilizamos `select_related("customer")`.

La finalidad es optimizar el acceso a la relación y evitar consultas adicionales innecesarias a la base de datos.

Regla sencilla:

```
ForeignKey
OneToOneField
        ↓
select_related()
```

## 10. prefetch_related()

`prefetch_related()` se utiliza principalmente con:

- `ManyToManyField`
- relaciones inversas
- relaciones que representan colecciones

Ejemplo:

```python
class OrderProductQuerySet(models.QuerySet):

    def with_products(self):
        return self.prefetch_related("products")
```

Como `products = models.ManyToManyField("Product")` representa varios productos, utilizamos `prefetch_related("products")`.

Regla sencilla:

```
ManyToMany
Relaciones inversas
        ↓
prefetch_related()
```

## 11. Regla rápida para recordar

| Relación         | Optimización          |
|------------------|------------------------|
| ForeignKey       | `select_related()`     |
| OneToOneField    | `select_related()`     |
| ManyToManyField  | `prefetch_related()`   |
| Relación inversa | `prefetch_related()`   |

## 12. Ejemplo completo con Employee

```python
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# QuerySet para consultas de Employee relacionadas con Company.
class EmployeeQuerySet(models.QuerySet):

    # Encapsulamos select_related() para reutilizar esta consulta.
    def from_company(self):
        return self.select_related("company")


class Employee(models.Model):
    name = models.CharField(max_length=100)

    # Campo FK: singular porque cada Employee pertenece a una Company.
    # Modelo relacionado: singular y comienza en mayúscula.
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    # Campo M2M: plural porque un Employee puede tener varias Hability.
    # Modelo relacionado: singular y comienza en mayúscula.
    habilities = models.ManyToManyField("Hability")

    def __str__(self):
        return self.name

    # Manager personalizado basado en el Custom QuerySet.
    objects = EmployeeQuerySet.as_manager()


class Hability(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
```

## 13. ¿Qué hace as_manager()?

Esta parte:

```python
objects = EmployeeQuerySet.as_manager()
```

conecta el Custom QuerySet con el modelo.

Podemos visualizarlo así:

```
Employee
   │
   ▼
objects
   │
   ▼
EmployeeQuerySet
   │
   ▼
from_company()
```

Por eso podemos escribir:

```python
Employee.objects.from_company()
```

En lugar de intentar:

```python
EmployeeQuerySet.from_company()
```

## 14. El QuerySet sigue teniendo sus métodos normales

Crear un Custom QuerySet no elimina los métodos normales de Django.

Por ejemplo:

```python
Employee.objects.all()
```

sigue funcionando.

También:

```python
Employee.objects.filter(name="Jhon")
```

y:

```python
Employee.objects.get(id=1)
```

Y además tenemos nuestro método:

```python
Employee.objects.from_company()
```

Por tanto:

```
Employee.objects
       │
       ├── all()
       ├── filter()
       ├── get()
       ├── exclude()
       ├── order_by()
       │
       └── from_company()
```

## 15. Flujo conceptual

La estructura puede entenderse como:

```
MODEL
  ↓
MANAGER
  ↓
QUERYSET
  ↓
MÉTODO DE CONSULTA
```

Por ejemplo:

```python
Employee.objects.from_company()
```

Significa conceptualmente:

```
Employee
   ↓
objects
   ↓
EmployeeQuerySet
   ↓
from_company()
```

Por eso la llamada se hace desde el modelo, utilizando el manager.

## 16. Método del modelo vs Custom QuerySet

Esta diferencia es importante.

### Método del modelo

Un método del modelo normalmente trabaja con una instancia específica.

Ejemplo:

```python
class Order(models.Model):

    total = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    def is_large(self):
        return self.total > 1000
```

Podemos utilizarlo así:

```python
order = Order.objects.get(id=1)

order.is_large()
```

Aquí:

```
order
 ↓
una instancia de Order
 ↓
is_large()
```

## 17. Custom QuerySet

Un Custom QuerySet normalmente trabaja con un conjunto de objetos.

Ejemplo:

```python
class OrderProductQuerySet(models.QuerySet):

    def with_products(self):
        return self.prefetch_related("products")
```

Esto devuelve pedidos:

```python
Order.objectsp.with_products()
```

Conceptualmente:

```
Order
 ├── Order
 ├── Order
 ├── Order
 └── Order
```

Por eso, si el ejercicio dice:

> "Crea otro método `with_products()` que traiga pedidos optimizados con sus productos."

Tiene sentido implementarlo como Custom QuerySet.

Estamos creando una consulta que devuelve un conjunto de `Order`.

## 18. Ejemplo completo Order / Customer / Product

```python
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# QuerySet para consultas de Order relacionadas con Customer.
class OrderCustomerQuerySet(models.QuerySet):

    # Encapsulamos select_related() para reutilizar esta consulta.
    def with_customer(self):
        return self.select_related("customer")


# QuerySet para consultas de Order relacionadas con Product.
class OrderProductQuerySet(models.QuerySet):

    # Encapsulamos prefetch_related() para reutilizar esta consulta.
    def with_products(self):
        return self.prefetch_related("products")


class Order(models.Model):

    # Campo FK: singular porque cada Order pertenece a un Customer.
    # Modelo relacionado: singular y comienza en mayúscula.
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    # Campo M2M: plural porque un Order puede tener varios Product.
    # Modelo relacionado: singular y comienza en mayúscula.
    products = models.ManyToManyField("Product")

    total = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    def __str__(self):
        return f"Numero de Orden #{self.customer.id}"

    # Managers personalizados basados en los QuerySets anteriores.
    objectsc = OrderCustomerQuerySet.as_manager()
    objectsp = OrderProductQuerySet.as_manager()


class Product(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
```

## 19. ¿Qué representan objectsc y objectsp?

En este ejemplo tenemos dos managers:

```python
objectsc = OrderCustomerQuerySet.as_manager()
objectsp = OrderProductQuerySet.as_manager()
```

Podemos visualizarlo:

```
Order
 │
 ├── objectsc
 │      ↓
 │   OrderCustomerQuerySet
 │      ↓
 │   with_customer()
 │
 └── objectsp
        ↓
     OrderProductQuerySet
        ↓
     with_products()
```

Por eso podemos hacer:

```python
Order.objectsc.with_customer()
```

y:

```python
Order.objectsp.with_products()
```

## 20. ¿Por qué no usamos simplemente objects?

Lo habitual en Django sería:

```python
objects = OrderQuerySet.as_manager()
```

Pero en nuestro ejercicio tenemos dos Custom QuerySets diferentes:

- `OrderCustomerQuerySet`
- `OrderProductQuerySet`

Por eso se utilizaron dos managers diferentes: `objectsc` y `objectsp`.

Los nombres podrían ser otros. Por ejemplo:

```python
customer_queries = OrderCustomerQuerySet.as_manager()
product_queries = OrderProductQuerySet.as_manager()
```

Y entonces:

```python
Order.customer_queries.with_customer()
Order.product_queries.with_products()
```

Los nombres `objectsc` y `objectsp` son válidos, aunque en un proyecto real conviene utilizar nombres más descriptivos.

## 21. Uso desde una vista

Para obtener los pedidos optimizados con el cliente:

```python
def list_order_customer(request):

    list_total = Order.objectsc.with_customer()

    return render(
        request,
        "list-order-customer.html",
        {"items": list_total}
    )
```

El flujo es:

```
Vista
 │
 ▼
Order
 │
 ▼
objectsc
 │
 ▼
with_customer()
 │
 ▼
QuerySet de Order
 │
 ▼
render()
```

## 22. Error: llamar directamente al Custom QuerySet

Una confusión común sería hacer:

```python
OrderCustomerQuerySet.with_customer()
```

Esto no es la forma normal de utilizarlo.

El método está definido en `OrderCustomerQuerySet`, pero ese QuerySet está conectado al modelo mediante:

```python
objectsc = OrderCustomerQuerySet.as_manager()
```

Por eso utilizamos:

```python
Order.objectsc.with_customer()
```

La relación es:

```
OrderCustomerQuerySet
        ↑
        │
    as_manager()
        │
        ↓
Order.objectsc
```

## 23. Error: pasar self manualmente

Tenemos:

```python
def with_customer(self):
    return self.select_related("customer")
```

No debemos llamar:

```python
Order.objectsc.with_customer(self)
```

El `self` lo proporciona Python automáticamente cuando se ejecuta el método.

Utilizamos:

```python
Order.objectsc.with_customer()
```

## 24. Error: confundir el modelo del QuerySet

Este:

```python
class OrderProductQuerySet(models.QuerySet):

    def with_products(self):
        return self.prefetch_related("products")
```

es un QuerySet de `Order`.

No es un QuerySet de `Product`.

¿Por qué? Porque está conectado a `Order` mediante:

```python
objectsp = OrderProductQuerySet.as_manager()
```

Por tanto:

```
OrderProductQuerySet
        ↓
QuerySet de Order
        ↓
with_products()
        ↓
Orders con sus Products optimizados
```

El nombre `OrderProductQuerySet` significa:

> QuerySet para consultas de Order relacionadas con Product.

No significa:

> QuerySet de Product.

## 25. ¿Qué devuelve with_products()?

Tenemos:

```python
def with_products(self):
    return self.prefetch_related("products")
```

El método devuelve un `QuerySet` de `Order` que ha sido preparado para acceder eficientemente a `order.products.all()`.

Por ejemplo:

```python
orders = Order.objectsp.with_products()

for order in orders:
    print(order.products.all())
```

La consulta principal sigue siendo sobre `Order`.

## 26. ¿El QuerySet pertenece a la View?

No.

La View utiliza el QuerySet, pero el QuerySet no pertenece a la View.

Por ejemplo:

```python
def list_order_customer(request):
    list_total = Order.objectsc.with_customer()
```

La View contiene más responsabilidades:

```
VIEW
 ├── recibe request
 ├── ejecuta consultas
 ├── procesa lógica
 └── devuelve response
```

El QuerySet es solamente una herramienta especializada para construir consultas.

Podemos visualizarlo:

```
VIEW
 │
 ├── request
 │
 ├── Order.objectsc.with_customer()
 │             │
 │             └── QuerySet
 │
 └── render()
```

## 27. QuerySet no es toda la View

Una View puede hacer muchas cosas:

```python
def list_orders(request):

    orders = Order.objects.filter(total__gt=100)

    return render(
        request,
        "orders.html",
        {"items": orders}
    )
```

Aquí, `Order.objects.filter(...)` es la parte relacionada con la consulta.

Pero la View también:

- recibe la petición,
- ejecuta la lógica,
- prepara el contexto,
- selecciona el template,
- devuelve la respuesta.

Por eso: el QuerySet es una parte de la lógica de acceso a datos; la View tiene responsabilidades adicionales.

## 28. ¿Por qué crear un Custom QuerySet?

Principalmente para reutilizar consultas y mantener la lógica de consultas organizada.

Sin Custom QuerySet:

```python
Order.objects.select_related("customer")
```

podría repetirse en diferentes partes del proyecto.

Con Custom QuerySet:

```python
Order.objectsc.with_customer()
```

tenemos una consulta reutilizable.

Esto permite:

```
Consulta repetitiva
       ↓
Custom QuerySet
       ↓
Método reutilizable
```

## 29. Ventaja principal

Supongamos que tenemos:

```python
def with_customer(self):
    return self.select_related("customer")
```

En lugar de repetir:

```python
Order.objects.select_related("customer")
```

podemos utilizar:

```python
Order.objectsc.with_customer()
```

Si posteriormente cambia la forma de optimizar esa consulta, podemos modificar el método en un único lugar.

## 30. Custom QuerySet + métodos encadenables

Una ventaja importante de los QuerySets es que sus consultas pueden encadenarse.

Por ejemplo:

```python
Order.objects.filter(total__gt=100).order_by("-total")
```

Un Custom QuerySet también puede participar en este tipo de composición.

Por ejemplo:

```python
Order.objectsp.with_products().filter(total__gt=100)
```

Conceptualmente:

```
Order
 ↓
objectsp
 ↓
with_products()
 ↓
filter()
 ↓
QuerySet final
```

Esto es una de las razones por las que los Custom QuerySets son útiles para encapsular consultas.

## 31. Diferencia fundamental

Podemos resumirlo así:

### Método del modelo

Trabaja normalmente con **UNA instancia**.

Ejemplo:

```python
order.is_large()
```

### Custom QuerySet

Trabaja normalmente con **UN CONJUNTO DE INSTANCIAS**.

Ejemplo:

```python
Order.objectsp.with_products()
```

## 32. Mapa mental completo

```
                         DJANGO ORM
                             │
             ┌───────────────┴───────────────┐
             │                               │
           MODEL                          MANAGER
             │                               │
             │                         objects / objectsc
             │                               │
             │                               ▼
             │                           QUERYSET
             │                               │
             │                    ┌──────────┴─────────┐
             │                    │                    │
             │                 Métodos             Custom
             │                 normales           QuerySet
             │                    │                    │
             │              all(), filter()    with_customer()
             │              get(), exclude()    with_products()
             │
             ├── ForeignKey
             │       │
             │       └── select_related()
             │
             └── ManyToMany
                     │
                     └── prefetch_related()
```

## 33. Ejemplo final resumido

```python
class OrderCustomerQuerySet(models.QuerySet):

    def with_customer(self):
        return self.select_related("customer")


class OrderProductQuerySet(models.QuerySet):

    def with_products(self):
        return self.prefetch_related("products")


class Order(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    products = models.ManyToManyField("Product")

    objectsc = OrderCustomerQuerySet.as_manager()
    objectsp = OrderProductQuerySet.as_manager()
```

Uso:

```python
Order.objectsc.with_customer()
```

y:

```python
Order.objectsp.with_products()
```

La lectura mental sería:

```
Order
 ↓
objectsc
 ↓
with_customer()
 ↓
QuerySet de Order
 ↓
select_related("customer")
```

Y:

```
Order
 ↓
objectsp
 ↓
with_products()
 ↓
QuerySet de Order
 ↓
prefetch_related("products")
```

## 34. Errores y correcciones aprendidos

| Confusión | Corrección |
|---|---|
| `customer` es el modelo | `customer` es el campo FK; `Customer` es el modelo |
| `customer_id` es el campo Django | Es normalmente la columna de BD |
| `products` es FK | `products` es `ManyToManyField` |
| `Product` es una tabla consecuencia de `Order` | Es una entidad independiente relacionada mediante M2M |
| QuerySet pertenece a la View | La View lo utiliza; el QuerySet es parte del ORM |
| QuerySet reemplaza a la View | No, la View tiene muchas más responsabilidades |
| Hay que pasar `self` desde la View | Python lo proporciona automáticamente |
| `OrderCustomerQuerySet.with_customer()` | Normalmente se accede mediante su manager |
| `Order.objectsc` es un QuerySet | Es el manager creado con `as_manager()` |
| `with_products()` devuelve Products | Devuelve un QuerySet de `Order` |
| Custom QuerySet elimina `.all()` | Los métodos normales siguen disponibles |
| `select_related()` para todo | FK/OneToOne → `select_related()` |
| `prefetch_related()` para todo | M2M/reverse → `prefetch_related()` |
| Método del modelo y Custom QuerySet son iguales | El primero suele trabajar con una instancia; el segundo con conjuntos |

## 35. Resumen final

### Model

Representa una entidad:

```python
class Order(models.Model):
    ...
```

### ForeignKey

Representa una relación hacia un objeto:

```python
customer = models.ForeignKey(Customer, ...)
```

### ManyToManyField

Representa una relación hacia varios objetos:

```python
products = models.ManyToManyField("Product")
```

### QuerySet

Representa un conjunto de objetos consultables:

```python
Order.objects.filter(...)
```

### Custom QuerySet

Permite crear métodos propios y reutilizables de consulta:

```python
class OrderProductQuerySet(models.QuerySet):

    def with_products(self):
        return self.prefetch_related("products")
```

### as_manager()

Conecta el Custom QuerySet con el modelo:

```python
objectsp = OrderProductQuerySet.as_manager()
```

### Uso

```python
Order.objectsp.with_products()
```

### Regla mental principal

```
MODELO
   ↓
MANAGER
   ↓
QUERYSET
   ↓
MÉTODO DE CONSULTA
```

Y para optimización:

```
ForeignKey / OneToOne
        ↓
select_related()


ManyToMany / relaciones inversas
        ↓
prefetch_related()
```
