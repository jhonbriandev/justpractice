from django.shortcuts import render
from .models import Book, Review


def w_reviews(request):
    reviews = Book.objects.filter(
            reviews__isnull=False
        ).distinct()
    return render(request,"list-book-review.html",{"list_reviews":reviews})
    
def list_book_author(request):
    list_a = Book.objects.all().select_related("author")
    return render(request,"list-author.html",{"list_authors":list_a})

def list_book_categories(request):
    list_c = Book.objects.all().prefetch_related("categories")
    return render(request,"list-category.html",{"list_categories":list_c})


def list_book_categories_author(request):
    list_c_a = Book.objects.all().prefetch_related("categories").select_related("author")
    return render (request,"list-category-author.html",{"items":list_c_a})