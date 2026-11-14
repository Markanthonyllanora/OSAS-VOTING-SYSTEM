from django.shortcuts import render


def admin_dashboard(request):
    return render(request, "OSAS/dashboard_admin.html", {
        "active_page": "dashboard",
        "page_title": "Dashboard",
    })