import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST


def _mock_candidates_by_position():
    return {
        "President": [
            {"initials": "JS", "name": "Juan Santos", "votes": 72, "pct": 33.0, "color": "#2563eb", "badge": "Leading"},
            {"initials": "MR", "name": "Maria Reyes", "votes": 58, "pct": 26.6, "color": "#8b5cf6", "badge": ""},
            {"initials": "LC", "name": "Lance Cruz", "votes": 45, "pct": 20.6, "color": "#10b981", "badge": ""},
            {"initials": "EG", "name": "Ella Garcia", "votes": 31, "pct": 14.2, "color": "#f59e0b", "badge": ""},
            {"initials": "RT", "name": "Rafael Torres", "votes": 12, "pct": 5.5, "color": "#ef4444", "badge": ""},
        ],
        "Vice President": [
            {"initials": "MR", "name": "Maria Reyes", "votes": 81, "pct": 37.2, "color": "#8b5cf6", "badge": "Leading"},
        ],
        "Secretary": [
            {"initials": "LC", "name": "Lance Cruz", "votes": 69, "pct": 31.7, "color": "#10b981", "badge": "Leading"},
        ],
        "Treasurer": [
            {"initials": "EG", "name": "Ella Garcia", "votes": 88, "pct": 40.4, "color": "#f59e0b", "badge": "Leading"},
        ],
        "Auditor": [
            {"initials": "RT", "name": "Rafael Torres", "votes": 64, "pct": 29.4, "color": "#ef4444", "badge": "Leading"},
        ],
        "P.R.O.": [
            {"initials": "SM", "name": "Sofia Mendoza", "votes": 77, "pct": 35.3, "color": "#3b82f6", "badge": "Leading"},
        ],
    }


def osas_ongoing_view(request):
    selected_position = request.GET.get("position", "President")
    selected_election = request.GET.get("election", "SSCC Election")
    positions = ["President", "Vice President", "Secretary", "Treasurer", "Auditor", "P.R.O."]
    by_pos = _mock_candidates_by_position()

    context = {
        "role": "osas",
        "active_page": "results",
        "selected_election": selected_election,
        "selected_position": selected_position,
        "positions": positions,
        "total_voters": 342,
        "votes_cast": 218,
        "turnout_pct": 63.7,
        "remaining_time": "2d 5h 32m",
        "candidates": by_pos.get(selected_position, by_pos["President"]),
        "recent_activity": [
            {"title": "New vote recorded", "subtitle": "Student #2025-0143", "time": "Apr 21, 2025 · 10:12 AM"},
            {"title": "Results updated", "subtitle": "President · 3 new votes", "time": "Apr 21, 2025 · 09:48 AM"},
        ],
    }
    return render(request, "results/osas_ongoing.html", context)


def osas_completed_view(request):
    selected_position = request.GET.get("position", "President")
    selected_election = request.GET.get("election", "SSCC Election")
    positions = ["President", "Vice President", "Secretary", "Treasurer", "Auditor", "P.R.O."]
    by_pos = _mock_candidates_by_position()

    winners_by_position = [
        {"position": "PRESIDENT", "initials": "JS", "name": "Juan Santos", "votes": 72, "pct": 33.0, "lead": "+14 lead"},
        {"position": "VICE PRESIDENT", "initials": "MR", "name": "Maria Reyes", "votes": 81, "pct": 37.2, "lead": "+19 lead"},
        {"position": "SECRETARY", "initials": "LC", "name": "Lance Cruz", "votes": 69, "pct": 31.7, "lead": "+9 lead"},
        {"position": "TREASURER", "initials": "EG", "name": "Ella Garcia", "votes": 88, "pct": 40.4, "lead": "+27 lead"},
        {"position": "AUDITOR", "initials": "RT", "name": "Rafael Torres", "votes": 64, "pct": 29.4, "lead": "+6 lead"},
        {"position": "P.R.O.", "initials": "SM", "name": "Sofia Mendoza", "votes": 77, "pct": 35.3, "lead": "+17 lead"},
    ]

    context = {
        "role": "osas",
        "active_page": "results",
        "selected_election": selected_election,
        "selected_position": selected_position,
        "positions": positions,
        "total_voters": 342,
        "votes_cast": 218,
        "did_not_vote": 124,
        "turnout_pct": 63.7,
        "positions_count": 6,
        "published": request.session.get("results_published", True),
        "winners_by_position": winners_by_position,
        "ranking": by_pos.get(selected_position, by_pos["President"]),
        "hourly_votes": [
            {"label": "8 AM", "count": 12, "height": 28},
            {"label": "9 AM", "count": 28, "height": 68},
            {"label": "10 AM", "count": 41, "height": 100},
            {"label": "11 AM", "count": 35, "height": 85},
            {"label": "12 PM", "count": 22, "height": 54},
            {"label": "1 PM", "count": 30, "height": 73},
            {"label": "2 PM", "count": 26, "height": 63},
            {"label": "3 PM", "count": 24, "height": 58},
        ],
    }
    return render(request, "results/osas_completed.html", context)


@require_POST
def toggle_publish_results(request):
    current = request.session.get("results_published", True)
    request.session["results_published"] = not current
    return redirect("results:osas_completed")


def export_results_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="election_results.csv"'
    writer = csv.writer(response)
    writer.writerow(["Position", "Candidate", "Votes", "Percentage"])
    for pos, rows in _mock_candidates_by_position().items():
        for r in rows:
            writer.writerow([pos, r["name"], r["votes"], f"{r['pct']}%"])
    return response


def export_results_pdf(request):
    return HttpResponse("PDF export placeholder ready.", content_type="text/plain")


def student_results_view(request):
    selected_position = request.GET.get("position", "President")
    positions = ["President", "Vice President", "Secretary", "Treasurer", "Auditor", "P.R.O."]
    by_pos = _mock_candidates_by_position()

    winners = [
        {"initials": "JS", "name": "Juan Santos", "position": "President", "pct": 33.0, "bg": "#dbeafe", "fg": "#1d4ed8"},
        {"initials": "MR", "name": "Maria Reyes", "position": "Vice President", "pct": 37.2, "bg": "#ede9fe", "fg": "#6d28d9"},
        {"initials": "LC", "name": "Lance Cruz", "position": "Secretary", "pct": 31.7, "bg": "#d1fae5", "fg": "#047857"},
        {"initials": "EG", "name": "Ella Garcia", "position": "Treasurer", "pct": 40.4, "bg": "#fef3c7", "fg": "#b45309"},
        {"initials": "RT", "name": "Rafael Torres", "position": "Auditor", "pct": 29.4, "bg": "#fee2e2", "fg": "#b91c1c"},
        {"initials": "SM", "name": "Sofia Mendoza", "position": "P.R.O.", "pct": 35.3, "bg": "#e0e7ff", "fg": "#4338ca"},
    ]

    context = {
        "role": "student",
        "active_page": "results",
        "selected_position": selected_position,
        "positions": positions,
        "turnout_pct": 63.7,
        "votes_cast": 218,
        "total_voters": 342,
        "published": request.session.get("results_published", True),
        "winners": winners,
        "position_candidates": by_pos.get(selected_position, by_pos["President"]),
    }
    return render(request, "results/student_results.html", context)
