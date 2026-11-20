from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    VISIBILITY_CHOICES = [
        ("all", "All Students"),
        ("election", "During Election Only"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateField(default=timezone.localdate)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="all")
    is_pinned = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_posted", "-id"]

    def __str__(self):
        return self.title