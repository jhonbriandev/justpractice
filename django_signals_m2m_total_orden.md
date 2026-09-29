# Clase: Signals `m2m_changed` en Django y cómo mantener el `total` de una Orden

> **Nivel:** principiante → intermedio
> **Tema:** relaciones ManyToMany, Signals, campo almacenado vs. método calculado, templates
> **Ejercicio de referencia:** una `Order` (orden) que tiene muchos `Product` (productos) y guarda su `total`.

---

## 0. Mapa de la clase

1. Vocabulario (sin tecnicismos escondidos)
2. El problema que se quería resolver
3. La solución: el código completo, explicado **por bloques**
4. La decisión clave: `{{ order.total }}` vs `{{ order.total_products }}`
5. ✅ Aciertos
6. ⚠️ Errores y puntos de mejora
7. 🧠 Aprendizajes clave
8. Ejercicios para practicar
9. Chuleta final (resumen de una página)

---

## 1. Vocabulario básico

| Término                          | Qué significa                                                                                                                                               | Analogía                                                                                                 |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **ManyToMany**                   | Una relación donde _muchos_ de un modelo se relacionan con _muchos_ de otro. Una orden tiene muchos productos, y un producto puede estar en muchas órdenes. | Un carrito de compras: el carrito tiene varios productos y cada producto puede estar en varios carritos. |
| **Tabla intermedia (`through`)** | Tabla que Django crea sola para guardar quién está relacionado con quién.                                                                                   | La lista de "renglones" de un recibo: cada renglón dice "esta orden ↔ este producto".                    |
| **Signal (señal)**               | Un aviso que Django emite cuando pasa algo (se guarda un objeto, cambia una relación, etc.).                                                                | Un timbre. Cuando alguien lo toca, suena y tú decides qué hacer.                                         |
| **Receiver (receptor)**          | La función que "escucha" una señal y reacciona.                                                                                                             | La persona que oye el timbre y abre la puerta.                                                           |
| **`instance`**                   | El objeto concreto afectado por la señal.                                                                                                                   | El cliente específico que tocó el timbre (no "los clientes" en general).                                 |
| **Campo del modelo**             | Una columna que se guarda en la base de datos (`total = models.DecimalField(...)`).                                                                         | Un número escrito con lapicero en el recibo.                                                             |
| **Método del modelo**            | Una función dentro del modelo que calcula algo cuando la llamas.                                                                                            | Una calculadora: te da el resultado cuando la usas, pero no lo deja escrito.                             |
| **Template**                     | El archivo HTML donde Django "pinta" los datos.                                                                                                             | El cartel que ve el cliente.                                                                             |

---

## 2. El problema

Cada vez que agregamos o quitamos productos de una orden, el **total** debe actualizarse solo.

Sin ayuda, tendríamos que acordarnos de recalcular el total en cada lugar del proyecto donde se modifiquen productos (vistas, admin, formularios...). Es fácil olvidarlo.

**Idea:** en vez de recordar, dejamos que Django nos _avise_ cada vez que la relación cambia. Eso es un **Signal**.

---

## 3. La solución, bloque por bloque

### 3.1 El método que calcula (en `models.py`)

```python
def total_products(self):
    total = 0
    for product in self.products.all():
        total += product.price
    return total
```

**Qué hace cada parte y por qué:**

- `def total_products(self):` → define un método _dentro del modelo `Order`_. `self` es "esta orden en particular".
- `total = 0` → empezamos con la caja registradora en cero.
- `self.products.all()` → pide todos los productos de _esta_ orden.
- `for product in ...: total += product.price` → recorremos uno por uno y sumamos el precio.
- `return total` → devuelve el resultado. **No lo guarda**, solo lo entrega.

> 💡 **Analogía:** es la calculadora. Suma, te da el número, y se olvida.

### 3.2 Los imports (en `signals.py`)

```python
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Order
```

- `m2m_changed` → el **tipo de timbre**: "cambió una relación ManyToMany".
- `receiver` → un **decorador** (una etiqueta que se pone encima de una función para darle un superpoder). Este superpoder es "conectar esta función a una señal".
- `Order` → el modelo que necesitamos para decirle a Django _cuál_ relación escuchar.

### 3.3 La conexión con la señal

```python
@receiver(m2m_changed, sender=Order.products.through)
```

- `@receiver(...)` → "esta función de abajo va a escuchar una señal".
- `m2m_changed` → "la señal que quiero escuchar".
- `sender=Order.products.through` → "solo escucha los cambios de **esta** relación: la tabla intermedia entre Order y Product".

> 💡 **Analogía:** sin `sender`, sería como abrir la puerta con _cualquier_ timbre del edificio. Con `sender`, solo respondes al timbre de tu departamento.

### 3.4 La función que reacciona

```python
def create_order(sender, instance, action, *args, **kwargs):
```

Django llama a esta función y le pasa información:

- `sender` → quién emitió la señal (la tabla intermedia).
- `instance` → el objeto afectado (la `Order`).
- `action` → **qué pasó** exactamente (ver siguiente bloque).
- `*args, **kwargs` → "cualquier otro dato extra que Django envíe". Los pones para que la función no falle si llegan datos que no usas (como `pk_set`, `reverse`, `model`, `using`).

### 3.5 El filtro por acción

```python
if action in ["post_add", "post_remove", "post_clear"]:
```

La señal `m2m_changed` suena **muchas veces** por cada cambio: antes y después de agregar, quitar o limpiar. Aquí decimos: "solo actúa **después** de que el cambio ya ocurrió".

| `action`                     | Significa                                         |
| ---------------------------- | ------------------------------------------------- |
| `pre_add` / `post_add`       | Antes / después de **agregar** productos          |
| `pre_remove` / `post_remove` | Antes / después de **quitar** productos           |
| `pre_clear` / `post_clear`   | Antes / después de **vaciar** todos los productos |

**¿Por qué `post_` y no `pre_`?** Porque si calculas _antes_ del cambio, el total sale con los productos viejos. Necesitas esperar a que la base de datos ya refleje la novedad.

### 3.6 Recalcular y guardar

```python
instance.total = instance.total_products()
instance.save()
```

- Línea 1: llamamos a la calculadora (`total_products()`) y **escribimos** el resultado en el campo `total`. Todavía solo está en memoria.
- Línea 2: `save()` lo **graba en la base de datos**. Sin esto, el total se perdería.

### 3.7 Código completo con comentarios

```python
# signals.py

# Señal que Django emite cuando cambia una relación ManyToMany
from django.db.models.signals import m2m_changed

# Decorador para conectar nuestra función con esa señal
from django.dispatch import receiver

# Modelo que contiene la relación ManyToMany con Product
from .models import Order


# "through" = tabla intermedia que Django crea automáticamente
@receiver(m2m_changed, sender=Order.products.through)
def create_order(sender, instance, action, *args, **kwargs):

    # Solo recalculamos DESPUÉS de que el cambio ya ocurrió
    if action in ["post_add", "post_remove", "post_clear"]:

        # instance = la Order afectada; total = campo guardado en BD
        instance.total = instance.total_products()

        # Guardamos para que el nuevo total quede en la base de datos
        instance.save()
```

### 3.8 Flujo completo (para memorizar)

```
Se agrega un producto a la orden
              ↓
        Django emite m2m_changed
              ↓
      action = "post_add"
              ↓
      instance = la Order
              ↓
   instance.total_products()   ← la calculadora
              ↓
     instance.total = resultado
              ↓
        instance.save()
              ↓
     BASE DE DATOS actualizada
              ↓
   Template muestra {{ order.total }}
```

---

## 4. La decisión clave: ¿`total` o `total_products`?

### La pregunta

En el template, ¿qué debo escribir?

```html
{{ order.total }}
```

o

```html
{{ order.total_products }}
```

### La respuesta: `{{ order.total }}`

|                           | `order.total`                       | `order.total_products`                 |
| ------------------------- | ----------------------------------- | -------------------------------------- |
| **Qué es**                | Campo guardado en la BD             | Método que calcula                     |
| **Qué hace al mostrarse** | Lee el valor ya guardado            | Vuelve a ejecutar la suma completa     |
| **Analogía**              | Leer el número escrito en el recibo | Volver a sumar todo con la calculadora |
| **Costo**                 | Muy barato                          | Consulta a la BD en cada visita        |

> 📝 **Dato útil de Django:** en los templates **no se ponen paréntesis** para llamar métodos. `{{ order.total_products }}` _sí ejecuta_ el método aunque no tenga `()`. Django lo llama automáticamente.

### Reparto de responsabilidades (lo bien diseñado)

| Pieza              | Responsabilidad               |
| ------------------ | ----------------------------- |
| `total_products()` | **Calcular**                  |
| `Signal`           | **Decidir cuándo** recalcular |
| Campo `total`      | **Guardar** el resultado      |
| Template           | **Mostrar** el resultado      |

Cada pieza hace **una sola cosa**. Esa idea se llama _separación de responsabilidades_ y es una señal de código limpio.

---

## 5. ✅ Aciertos

1. **Separar el cálculo del guardado.** Meter la suma en un método (`total_products()`) y no dentro del signal hace el código reutilizable y más fácil de probar.
2. **Usar `sender=Order.products.through`.** Evita que la función reaccione a relaciones que no tienen nada que ver.
3. **Usar solo las acciones `post_*`.** Se calcula cuando los datos ya están actualizados.
4. **Cubrir las tres acciones** (`add`, `remove`, `clear`). Muchos principiantes solo cubren `add` y el total queda mal cuando se quita un producto.
5. **Mostrar `{{ order.total }}` en el template.** El template no repite trabajo: solo presenta.
6. **Entender el "porqué"** y no solo copiar el código: saber que el campo es el _resultado_ y el método es el _cálculo_.

---

## 6. ⚠️ Errores y puntos de mejora

> Nota: estos puntos salen del código y la conversación de esta clase. Son cosas que **conviene corregir o vigilar**, no fallos graves. El código del ejercicio funciona para el caso básico.

### 6.1 Nombre engañoso de la función

```python
def create_order(...)   # ❌ el nombre dice "crear orden", pero la función NO crea nada
```

**Mejor:**

```python
def update_order_total(...)   # ✅ dice exactamente lo que hace
```

> 💡 Un buen nombre es un comentario gratis. Dentro de 3 meses vas a agradecerlo.

### 6.2 Formato del decorador

```python
@receiver (m2m_changed,sender = Order.products.through)   # ❌ funciona, pero se ve desordenado
```

```python
@receiver(m2m_changed, sender=Order.products.through)     # ✅ estilo estándar de Python (PEP 8)
```

Reglas rápidas: sin espacio antes del paréntesis, espacio después de cada coma, y **sin espacios** alrededor del `=` en argumentos con nombre.

### 6.3 Olvidar registrar el signal (error clásico)

Un signal en `signals.py` **no funciona solo**. Django tiene que "enterarse" de que existe. Lo más común es importarlo en `apps.py`:

```python
# apps.py
from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        # Importar signals aquí hace que Django los registre al arrancar
        from . import signals  # noqa: F401
```

> 💡 **Analogía:** escribir la función es contratar al portero; importar `signals` en `ready()` es **decirle en qué puerta trabaja**. Si no, el timbre suena y nadie contesta.

### 6.4 Cuando el cambio viene "del otro lado" (`reverse`)

La relación se puede modificar de dos maneras:

```python
order.products.add(product)        # desde la Order  → instance = Order ✅
product.order_set.add(order)       # desde el Product → instance = Product ⚠️
```

En el segundo caso, `instance` es un `Product`, y `instance.total_products()` fallaría (los productos no tienen ese método). Django lo avisa con el argumento `reverse`.

Versión más segura para cuando lo necesites:

```python
@receiver(m2m_changed, sender=Order.products.through)
def update_order_total(sender, instance, action, reverse, pk_set, **kwargs):
    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    if not reverse:
        # El cambio se hizo desde la Order: instance ES la orden
        orders = [instance]
    else:
        # El cambio se hizo desde el Product: pk_set trae los ids de las órdenes
        orders = Order.objects.filter(pk__in=pk_set or [])

    for order in orders:
        order.total = order.total_products()
        order.save(update_fields=["total"])
```

> Para empezar, **no es obligatorio**. Basta con saberlo para no sorprenderte cuando un día falle.

### 6.5 El total guardado puede quedar desactualizado

El signal reacciona cuando **cambia la relación** (se agrega o quita un producto). Pero **no** reacciona si, por ejemplo, **cambias el precio de un producto** que ya estaba en una orden.

Resultado: `order.total` mostraría un número viejo.

| Enfoque                                         | Ventaja            | Desventaja                                         |
| ----------------------------------------------- | ------------------ | -------------------------------------------------- |
| **Campo guardado + signal** (lo que hicimos)    | Lectura muy rápida | Puede quedar desactualizado si cambian otros datos |
| **Método o `@property` que calcula al momento** | Siempre correcto   | Repite la consulta cada vez                        |

**¿Cuál es el más común para principiantes?** El método o `@property` sin signals, porque es más simple y no hay nada que se desincronice. Lo que hiciste (campo + signal) es un ejercicio excelente para **aprender signals**, y es útil de verdad cuando necesitas leer totales muchas veces o filtrar/ordenar por total.

### 6.6 Sumar con un `for` vs. con `Sum`

```python
# Versión actual: clara y perfecta para aprender
total = 0
for product in self.products.all():
    total += product.price
return total
```

```python
# Versión más profesional: la base de datos hace la suma
from django.db.models import Sum

def total_products(self):
    result = self.products.aggregate(total=Sum("price"))
    return result["total"] or 0
```

- `aggregate(total=Sum("price"))` → pide a la base de datos: "suma la columna `price`".
- `["total"]` → saca el valor del diccionario que devuelve.
- `or 0` → si la orden no tiene productos, el resultado es `None`; con `or 0` lo convertimos en cero.

**¿Cuál es el más común para principiantes?** El `for`, porque se lee como una frase y se entiende al instante. Cuando el proyecto crece, se pasa a `Sum`, que es más rápido porque no trae todos los productos a Python.

### 6.7 Cuidado con `save()` dentro de signals

`instance.save()` dispara otros signals de guardado (`post_save`). Si algún día tienes un signal `post_save` en `Order` que también hace `save()`, puedes crear un **bucle infinito** (guardo → señal → guardo → señal...).

Formas de reducir el riesgo:

```python
instance.save(update_fields=["total"])  # guarda solo esa columna
```

o usar `Order.objects.filter(pk=instance.pk).update(total=nuevo_total)`, que guarda sin disparar `post_save`.

---

## 7. 🧠 Aprendizajes clave

1. **Campo ≠ método.** El campo _guarda_; el método _calcula_. Confundirlos es el error más común al empezar.
2. **Un signal es un aviso, no una orden.** Solo dice "esto pasó"; tú decides qué hacer.
3. **`instance` = el objeto concreto afectado.** No "todas las órdenes".
4. **`post_` significa "ya ocurrió".** Para calcular sobre datos actualizados, usa `post_`.
5. **Los templates ejecutan métodos sin paréntesis.** `{{ order.total_products }}` sí calcula.
6. **El template debe mostrar, no calcular.** La lógica va en el modelo.
7. **Un signal debe registrarse** (normalmente en `apps.py` → `ready()`).
8. **Nombres claros > comentarios.** `update_order_total` explica más que `create_order`.
9. **Todo dato guardado puede desactualizarse.** Piensa siempre: "¿qué otros cambios podrían volver viejo este número?".
10. **Existen varias formas correctas.** Elegir la más simple que resuelva el problema suele ser la mejor decisión para empezar.

---

## 8. Ejercicios para practicar

1. **Renombra** la función `create_order` a `update_order_total` y verifica que todo sigue funcionando.
2. **Prueba en el shell** (`python manage.py shell`):
   ```python
   order = Order.objects.create()
   order.products.add(producto1, producto2)
   order.refresh_from_db()
   print(order.total)
   order.products.remove(producto1)
   order.refresh_from_db()
   print(order.total)
   order.products.clear()
   order.refresh_from_db()
   print(order.total)   # debería ser 0
   ```
   > `refresh_from_db()` vuelve a leer la orden desde la BD para ver el valor guardado.
3. **Provoca el problema 6.5:** cambia el precio de un producto ya incluido en una orden y observa que `order.total` no se actualiza. Luego piensa cómo lo resolverías.
4. **Cambia el `for` por `aggregate(Sum(...))`** y compara resultados.
5. **Agrega un `print(action)`** dentro del signal y observa cuántas veces y con qué valores suena al agregar un producto.
6. **Reto:** crea un segundo signal que, además del total, actualice un campo `items_count` con la cantidad de productos de la orden.

---

## 9. Chuleta final

```
ManyToMany cambia
      ↓
   Signal (m2m_changed)
      ↓
   ¿action es post_add / post_remove / post_clear?
      ↓
   instance.total = instance.total_products()   ← calcula
      ↓
   instance.save()                               ← guarda
      ↓
   Template: {{ order.total }}                   ← muestra
```

**Reglas de oro:**

- El **modelo** calcula.
- El **signal** decide cuándo.
- El **campo** guarda.
- El **template** muestra.

**Checklist antes de dar por terminado un signal:**

- [ ] ¿Está registrado en `apps.py` → `ready()`?
- [ ] ¿Usa `sender=` para escuchar solo lo necesario?
- [ ] ¿Filtra por `action` con `post_*`?
- [ ] ¿El nombre de la función dice lo que hace?
- [ ] ¿Qué pasa si el cambio viene del lado contrario (`reverse`)?
- [ ] ¿Qué otros cambios podrían dejar el total desactualizado?

##Resumen para responder en tu entrevista oral:
Para el modelo: "Definí un Custom QuerySet en el modelo y lo asigné al Manager del objeto."

Para la vista: "En la vista ejecuto una consulta ORM llamando al método de nuestro Custom QuerySet, lo cual me devuelve un QuerySet optimizado.##
