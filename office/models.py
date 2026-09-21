from django.db import models

class Apartment(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class ProjectQuerySet(models.QuerySet):
    def with_apartment(self):
        return self.select_related("apartment")
    
    def with_collaborator(self):
        return self.prefetch_related("collaborators")

class Project(models.Model):
    name = models.CharField(max_length=100)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    collaborators = models.ManyToManyField('Collaborator')

    def __str__(self):
        return self.name
    
    objects = ProjectQuerySet.as_manager()
    
class Collaborator(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name