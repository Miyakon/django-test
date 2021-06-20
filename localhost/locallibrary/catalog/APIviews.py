import json

from django.contrib.auth.models import Group, User
from django.http.response import HttpResponse
from rest_framework import permissions, viewsets

from catalog.models import Author, Book, BookInstance, Genre
from catalog.serializers import (AuthorSerializer, BookSerializer,
                                 GenreSerializer, GroupSerializer,
                                 UserSerializer)


def api(request):
    """ Return Hello World """
    message = {
    "message": "Hello World!"
}
    message_json = json.dumps(message)
    return HttpResponse(message_json)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

class GenreViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows genres to be viewed or edited.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticated]

class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows authors to be viewed or edited.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]
