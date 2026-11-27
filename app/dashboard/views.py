from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils import timezone

from app.announcements.models import Announcement
from app.elections.models import Candidate, Voter
from app.manage_elections.models import Election

User = get_user_model()


def _election_kind(title):
    t = title.lower()
    if "ssc" in t or "supreme" in t:
        return "ssc"
    if "campus" in t:
        return "campus"
    if "department" in t or "dept" in t:
        return "department"
    return "generic"


def _decorate(election, now):
    election.status = election.get_status()
    election.kind = _election_kind(election.title)
    total = (election.end_date - election.start_date).total_seconds()
    elapsed = (now - election.start_date).total_seconds()
    election.progress = int(max(0, min(100, (elapsed / total) * 100))) if total > 0 else 0
    return election


def _current_election(now):
    ongoing = Election.objects.filter(start_date__lte=now, end_date__gte=now).order_by("end_date").first()
    if ongoing:
        return ongoing
    upcoming = Election.objects.filter(start_date__gt=now).order_by("start_date").first()
    if upcoming:
        return upcoming
    return Election.objects.order_by("-end_date").first()


@staff_member_required(login_url="/accounts/login/")
def admin_dashboard(request):
    now = timezone.now()

    elections = Election.objects.all()
    ongoing_count = elections.filter(start_date__lte=now, end_date__gte=now).count()
    upcoming_count = elections.filter(start_date__gt=now).count()
    closed_count = elections.filter(end_date__lt=now).count()

    current = _current_election(now)
    if current:
        _decorate(current, now)

    recent_elections = [_decorate(e, now) for e in elections.order_by("-start_date")[:5]]

    cand_rows = Candidate.objects.values("election").annotate(total=Count("id")).order_by("-total")
    election_labels = dict(Candidate.ELECTION_CHOICES)
    cand_max = max([r["total"] for r in cand_rows], default=0)
    candidates_by_election = [
        {
            "label": election_labels.get(r["election"], r["election"]),
            "total": r["total"],
            "pct": int(r["total"] / cand_max * 100) if cand_max else 0,
        }
        for r in cand_rows
    ]

    voter_rows = Voter.objects.values("department").annotate(total=Count("id")).order_by("-total")
    voter_max = max([r["total"] for r in voter_rows], default=0)
    voters_by_department = [
        {
            "label": r["department"],
            "total": r["total"],
            "pct": int(r["total"] / voter_max * 100) if voter_max else 0,
        }
        for r in voter_rows
    ]

    stats = {
        "elections": elections.count(),
        "ongoing": ongoing_count,
        "upcoming": upcoming_count,
        "closed": closed_count,
        "candidates": Candidate.objects.count(),
        "active_candidates": Candidate.objects.filter(status="active").count(),
        "voters": Voter.objects.count(),
        "active_voters": Voter.objects.filter(status="active").count(),
        "student_accounts": User.objects.filter(is_staff=False).count(),
        "pending_admins": User.objects.filter(is_staff=True, is_active=False).count(),
    }

    return render(request, "OSAS/dashboard_admin.html", {
        "active_page": "dashboard",
        "page_title": "Dashboard",
        "stats": stats,
        "current": current,
        "recent_elections": recent_elections,
        "candidates_by_election": candidates_by_election,
        "voters_by_department": voters_by_department,
        "announcements": Announcement.objects.all()[:5],
    })


@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect("dashboard:admin_dashboard")

    now = timezone.now()

    current = _current_election(now)
    if current:
        _decorate(current, now)

    ongoing = list(Election.objects.filter(start_date__lte=now, end_date__gte=now).order_by("end_date"))
    upcoming = list(Election.objects.filter(start_date__gt=now).order_by("start_date"))
    upcoming_elections = [_decorate(e, now) for e in (ongoing + upcoming)[:3]]

    announcements = Announcement.objects.filter(is_published=True)
    if not ongoing:
        announcements = announcements.exclude(visibility="election")
    announcements = announcements.order_by("-is_pinned", "-date_posted", "-id")[:3]

    return render(request, "STUDENT/dashboard_student.html", {
        "active_page": "dashboard",
        "page_title": "Dashboard",
        "current": current,
        "upcoming_elections": upcoming_elections,
        "announcements": announcements,
    })