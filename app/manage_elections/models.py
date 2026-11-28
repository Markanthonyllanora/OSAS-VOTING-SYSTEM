
from django.db import models


class Election(models.Model):

    ELECTION_CHOICES = [
        ("SSC", "SSC"),
        ("CAMPUS", "Campus"),
        ("DEPARTMENT", "Department"),
    ]

    DEPARTMENT_CHOICES = [
        ("ABELS", "ABELS"),
        ("BSA", "BSA"),
        ("BSAIS", "BSAIS"),
        ("BSE", "BSE"),
        ("BSIT", "BSIT"),
        ("BSPA", "BSPA"),
        ("BSSW", "BSSW"),
        ("BTVTEd", "BTVTEd"),
        ("DHRS", "DHRS"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    election_type = models.CharField(
        max_length=20,
        choices=ELECTION_CHOICES,
        default="SSC"
    )

    department = models.CharField(
        max_length=30,
        choices=DEPARTMENT_CHOICES,
        blank=True
    )

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
