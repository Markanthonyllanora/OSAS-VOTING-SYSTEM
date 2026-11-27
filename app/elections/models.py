from django.db import models


class Candidate(models.Model):
    POSITION_CHOICES = [
        ("President", "President"),
        ("Vice President", "Vice President"),
        ("Secretary", "Secretary"),
        ("Treasurer", "Treasurer"),
        ("Auditor", "Auditor"),
        ("Representative", "Representative"),
    ]
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
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    middle_initial = models.CharField(max_length=2, blank=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    election = models.CharField(max_length=20, choices=ELECTION_CHOICES)
    department = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    biography = models.TextField(blank=True)
    photo = models.ImageField(upload_to="candidates/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self):
        mi = self.middle_initial.strip().rstrip(".")
        if mi:
            return f"{self.first_name} {mi}. {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.position})"


class Voter(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    voter_id = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    middle_initial = models.CharField(max_length=2, blank=True)
    department = models.CharField(max_length=30, choices=Candidate.DEPARTMENT_CHOICES)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self):
        mi = self.middle_initial.strip().rstrip(".")
        if mi:
            return f"{self.first_name} {mi}. {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.voter_id} - {self.full_name}"