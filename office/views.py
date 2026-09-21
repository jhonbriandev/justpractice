from django.shortcuts import render
from .models import Project


def list_project_apartment_collaborator(request):
    list_projects = Project.objects.with_apartment().with_collaborator()
    return render (request,"list-project-apartment-collaborator.html",{"items":list_projects})
