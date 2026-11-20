from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "content", "visibility", "is_pinned", "is_important", "is_published"]
        labels = {
            "content": "Message",
            "is_pinned": "Pin this announcement",
            "is_important": "Mark as important",
            "is_published": "Publish Now",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "modal-input"}),
            "content": forms.Textarea(attrs={"class": "modal-input", "rows": 4}),
            "visibility": forms.RadioSelect(),
        }