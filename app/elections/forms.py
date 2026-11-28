from django import forms
from app.manage_elections.models import Election

from .models import Candidate, Voter



class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = [
            "first_name", "last_name", "middle_initial",
            "position", "party_name", "slogan",
            "election", "department", "status",
            "biography", "photo",
        ]
        labels = {"middle_initial": "M.I."}
        widgets = {"biography": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["position"].choices = [
            ("", "Select Position")
        ] + list(Candidate.POSITION_CHOICES)

        self.fields["election"].choices = [
            ("", "Select Election Type")
        ] + list(Candidate.ELECTION_CHOICES)

        self.fields["department"].choices = [
            ("", "Select Department")
        ] + list(Candidate.DEPARTMENT_CHOICES)

        self.fields["department"].required = False

    def clean(self):
        cleaned = super().clean()

        if cleaned.get("election") == "DEPARTMENT":
            if not cleaned.get("department"):
                self.add_error("department", "Please select a department.")
        else:
            cleaned["department"] = ""

        return cleaned



class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = [
            "voter_id", "first_name", "last_name", "middle_initial",
            "department", "email", "status",
        ]
        labels = {"middle_initial": "M.I."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].choices = [("", "Select Department")] + list(Candidate.DEPARTMENT_CHOICES)
        self.fields["voter_id"].widget.attrs["placeholder"] = "e.g. 2026-0001"

    def clean_voter_id(self):
        # Compare IDs without surrounding spaces / case differences
        voter_id = self.cleaned_data["voter_id"].strip().upper()
        duplicates = Voter.objects.filter(voter_id__iexact=voter_id)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("A voter with this ID already exists.")
        return voter_id

    def clean_email(self):
        # Emails are case-insensitive, so store them lowercase
        email = self.cleaned_data["email"].strip().lower()
        duplicates = Voter.objects.filter(email__iexact=email)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("A voter with this email already exists.")
        return email