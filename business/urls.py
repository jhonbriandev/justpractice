from django.contrib import admin
from django.urls import path, include
from .import views
 
urlpatterns = [
    path('employees/', views.employee_company , name = "index"),
    path('employees-habilities/', views.employee_habilitiy, name = "index")
]