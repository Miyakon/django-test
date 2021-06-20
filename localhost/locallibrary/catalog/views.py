import datetime
import json

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rest_framework import permissions, viewsets

from catalog.forms import RenewBookForm
from catalog.models import Author, Book, BookInstance, Genre
from catalog.serializers import (AuthorSerializer, BookSerializer,
                                 GenreSerializer, GroupSerializer,
                                 UserSerializer)

# Create your views here.


def index(request):
    """ View function for home page of site."""

    # Generate couts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    # Filter Genre books
    num_dorama = Book.objects.filter(genre__name__icontains='science').count()
    # num_dorama = Book.objects.filter(genre__contains='dorama').count()
    # num_dorama = Book.objects.filter(genre__exact='dorama').count()

    with open('/etc/map_token.txt') as f:
        map_token = f.read().strip()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_dorama': num_dorama,
        'num_visits': num_visits,
        'map_token': map_token,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 3
    # context_object_name = 'my_book_list'   # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    # template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(generic.DetailView):
    model = Author

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        author_id = self.request.path.split('/')[-1]
        works = Book.objects.filter(author__id__exact=author_id)
        context['works'] = works
        return context


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class BorrowedListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    """ Generic class-based view listing book borrowed. """
    model = BookInstance
    template_name = 'catalog/borrowed_list.html'
    paginate_by = 10
    permission_required = ('catalog.can_view_borrowed')

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o')


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class PermissionLibrarian(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = ('catalog.can_view_borrowed')


class AuthorCreate(PermissionLibrarian, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}


class AuthorUpdate(PermissionLibrarian, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'


class AuthorDelete(PermissionLibrarian, DeleteView):
    model = Author
    success_url = reverse_lazy('author')


class BookCreate(PermissionLibrarian, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']
    initial = {'Summary': 'Summary'}


class BookUpdate(PermissionLibrarian, UpdateView):
    model = Book
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'


class BookDelete(PermissionLibrarian, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
