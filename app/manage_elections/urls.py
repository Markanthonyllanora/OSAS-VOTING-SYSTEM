
from django.urls import path
from . import views

urlpatterns = [
    path('', views.manage_elections, name='manage_elections'),
    path('create/', views.create_election, name='create_election'),
    path('delete/<int:election_id>/', views.delete_election, name='delete_election'),
]
