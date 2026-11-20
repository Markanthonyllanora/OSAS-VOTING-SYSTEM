from django.urls import path

from . import views

app_name = "elections"

urlpatterns = [
    path("candidates/", views.manage_candidates, name="manage_candidates"),
    path("candidates/<int:pk>/edit/", views.candidate_edit, name="candidate_edit"),
    path("candidates/<int:pk>/delete/", views.candidate_delete, name="candidate_delete"),
]