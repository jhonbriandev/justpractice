from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class ArticleAuthorQuerySet(models.QuerySet):
    def with_author(self):
        # self representa el QuerySet actual obtenido desde el Manager (objects).
        return self.select_related("author")
    
class ArticleLabelQuerySet(models.QuerySet):
    def with_label(self):
        return self.prefetch_related("labels")

class Article(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    labels = models.ManyToManyField('Label')

    def __str__(self):
        return self.name
    
    objects_author = ArticleAuthorQuerySet.as_manager()
    objects_label = ArticleLabelQuerySet.as_manager()
    
class Label(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name