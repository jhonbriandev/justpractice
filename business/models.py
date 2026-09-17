from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class EmployeeQuerySet(models.QuerySet):
    # En lugar de repetir:
    # Employee.objects.all().select_related("company")
    # puedes hacer:
    # Employee.objects.from_company()
    
    # Obtiene los empleados cargando su Company mediante JOIN.
    def from_company(self):
        return self.select_related("company")

    # Employee.objects.from_company()
    #                 ↓
    # EmployeeQuerySet.from_company()
    #                 ↓
    # select_related("company")


class Employee(models.Model):
    name = models.CharField(max_length=100)

    # Relación muchos empleados → una compañía.
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    # Relación muchos empleados ↔ muchas habilidades.
    habilities = models.ManyToManyField("Hability")

    def __str__(self):
        return self.name

    # Reemplaza el Manager predeterminado por uno basado en EmployeeQuerySet.
    objects = EmployeeQuerySet.as_manager()


class Hability(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
 
