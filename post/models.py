from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Article(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    labels = models.ManyToManyField('Label')

    def __str__(self):
        return self.author
    
class Label(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name