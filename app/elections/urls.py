from django.urls import path
from . import views

app_name = "results"

urlpatterns = [
    # OSAS Results Routes
    path("osas/results/ongoing/", views.osas_ongoing_view, name="osas_ongoing"),
    path("osas/results/completed/", views.osas_completed_view, name="osas_completed"),
    path("osas/results/toggle-publish/", views.toggle_publish_results, name="toggle_publish"),
    path("osas/results/export/csv/", views.export_results_csv, name="export_csv"),
    path("osas/results/export/pdf/", views.export_results_pdf, name="export_pdf"),

    # Student Results Route
    path("student/results/", views.student_results_view, name="student_results"),
]
