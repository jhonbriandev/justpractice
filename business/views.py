from django.shortcuts import render
from .models import Employee


def employee_company(request):

    # Obtiene todos los empleados y carga su Company en la misma consulta SQL.
    employees = Employee.objects.all().select_related("company")

    return render(request, "employee-company.html", {"items": employees})


def employee_habilitiy(request):

    # Obtiene todos los empleados y precarga la relación indicada.
    habilities = Employee.objects.all().prefetch_related("habilities")

    return render(request, "employee-hability.html", {"items": habilities})

