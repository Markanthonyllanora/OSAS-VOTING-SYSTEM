from django import forms

from .models import Candidate


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = [
            "first_name", "last_name", "middle_initial",
            "position", "election", "status", "biography", "photo",
        ]
        labels = {"middle_initial": "M.I"}
        widgets = {"biography": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Placeholder option shown first in the dropdowns
        self.fields["position"].choices = [("", "Select Position")] + list(Candidate.POSITION_CHOICES)
        self.fields["election"].choices = [("", "Select Election")] + list(Candidate.ELECTION_CHOICES)