from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category')
    
    def __str__(self):
        return self.title
    
class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    qualification = models.IntegerField()
    
    def __str__(self):
        return self.book.title

# Desde	Hacia	Dirección	    Cómo
# Review	    Book	➡️     Adelante	review.book
# Book	        Review	⬅️     Atrás/inversa	book.reviews.all()
# Book.objects	Review	⬅️     Atrás/inversa en consulta	filter(reviews__...)

# La FK determina la dirección "hacia adelante".
# related_name te da un nombre para recorrer la relación "hacia atrás".