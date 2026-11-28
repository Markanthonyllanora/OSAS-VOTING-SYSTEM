from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .forms import AnnouncementForm
from .models import Announcement


@login_required
def student_announcements(request):
    query = request.GET.get("q", "").strip()
    announcements = Announcement.objects.filter(is_published=True)

    pinned = announcements.filter(is_pinned=True).first()
    others = announcements.exclude(pk=pinned.pk) if pinned else announcements

    if query:
        others = others.filter(Q(title__icontains=query) | Q(content__icontains=query))

    return render(request, "STUDENT/announcement_student.html", {
        "pinned": pinned,
        "announcements": others,
        "query": query,
        "active_page": "announcements",
        "page_title": "Announcements",
    })


@staff_member_required
def admin_announcements(request):
    show_modal = False

    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("announcements:admin_list")
        show_modal = True
    else:
        form = AnnouncementForm()

    query = request.GET.get("q", "").strip()
    announcements = Announcement.objects.all()

    pinned = announcements.filter(is_pinned=True).first()
    others = announcements.exclude(pk=pinned.pk) if pinned else announcements

    if query:
        others = others.filter(Q(title__icontains=query) | Q(content__icontains=query))

    return render(request, "OSAS/announcement_admin.html", {
        "pinned": pinned,
        "announcements": others,
        "query": query,
        "form": form,
        "show_modal": show_modal,
        "active_page": "announcements",
        "page_title": "Announcements",
    })


@login_required
def announcement_detail(request, pk):
    if request.user.is_staff:
        announcement = get_object_or_404(Announcement, pk=pk)
    else:
        announcement = get_object_or_404(Announcement, pk=pk, is_published=True)

    return render(request, "STUDENT/announcement_detail.html", {
        "announcement": announcement,
        "active_page": "announcements",
        "page_title": "Announcements",
    })