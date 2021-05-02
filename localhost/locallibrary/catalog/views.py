from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre

# Create your views here.
def index (request):
    """ View function for home page of site."""

    # Generate couts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Filter Genre books
    # num_dorama = Book.objects.filter(genre__exact='dorama').count()
    num_dorama = Book.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_dorama': num_dorama,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)
