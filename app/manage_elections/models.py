
from django.db import models


class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_status(self):
        from django.utils import timezone

        now = timezone.now()

        if now < self.start_date:
            return "Upcoming"
        elif now <= self.end_date:
            return "Ongoing"
        else:
            return "Closed"
