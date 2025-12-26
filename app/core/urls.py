from django.urls import path
from .views import hello, index

urlpatterns = [
    path('', index, name='index'),
    path('hello/', hello, name='hello'),
]
