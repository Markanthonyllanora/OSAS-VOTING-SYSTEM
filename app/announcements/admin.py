from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "date_posted", "visibility", "is_pinned", "is_important", "is_published")
    list_filter = ("visibility", "is_pinned", "is_important", "is_published")
    search_fields = ("title", "content")