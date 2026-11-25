from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@staff_member_required(login_url="/accounts/login/")
def admin_dashboard(request):
    return render(request, "OSAS/dashboard_admin.html", {
        "active_page": "dashboard",
        "page_title": "Dashboard",
    })


@login_required
def student_dashboard(request):
    return render(request, "STUDENT/dashboard_student.html", {
        "active_page": "dashboard",
        "page_title": "Dashboard",
    })