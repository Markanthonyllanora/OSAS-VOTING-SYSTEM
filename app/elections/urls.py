from django.urls import path

from . import views

app_name = "elections"

urlpatterns = [
    path("candidates/", views.manage_candidates, name="manage_candidates"),
    path("candidates/<int:pk>/edit/", views.candidate_edit, name="candidate_edit"),
    path("candidates/<int:pk>/delete/", views.candidate_delete, name="candidate_delete"),
    path("voters/", views.manage_voters, name="manage_voters"),
    path("voters/import/", views.voter_import, name="voter_import"),
    path("voters/import/template/", views.voter_import_template, name="voter_import_template"),
    path("voters/<int:pk>/edit/", views.voter_edit, name="voter_edit"),
    path("voters/<int:pk>/delete/", views.voter_delete, name="voter_delete"),
]