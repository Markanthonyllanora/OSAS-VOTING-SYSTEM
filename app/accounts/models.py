from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [("student", "Student Voter"), ("admin", "OSAS Admin")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")
    middle_initial = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"