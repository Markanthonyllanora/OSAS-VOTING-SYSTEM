from django.urls import path
from . import views

app_name = "announcements"

urlpatterns = [
    path("", views.student_announcements, name="student_list"),
    path("manage/", views.admin_announcements, name="admin_list"),
    path("<int:pk>/", views.announcement_detail, name="detail"),
]