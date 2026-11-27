from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CandidateForm, VoterForm
from .importers import TEMPLATE_HEADER, TEMPLATE_ROWS, import_voters
from .models import Candidate, Voter


@staff_member_required
def manage_candidates(request):
    # The Add Candidate popup posts back to this same page.
    form = CandidateForm(request.POST or None, request.FILES or None)
    open_modal = False

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate added.")
            return redirect("elections:manage_candidates")
        open_modal = True  # reopen the popup so the errors are visible

    candidates = Candidate.objects.all()
    q = request.GET.get("q", "").strip()
    position = request.GET.get("position", "")
    if q:
        candidates = candidates.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )
    if position:
        candidates = candidates.filter(position=position)

    return render(request, "OSAS/manage_candidates.html", {
        "active_page": "candidates",
        "page_title": "Manage Candidates",
        "candidates": candidates,
        "q": q,
        "selected_position": position,
        "positions": Candidate.POSITION_CHOICES,
        "form": form,
        "open_modal": open_modal,
    })


@staff_member_required
def candidate_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    form = CandidateForm(request.POST or None, request.FILES or None, instance=candidate)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Candidate updated.")
        return redirect("elections:manage_candidates")

    return render(request, "OSAS/candidate_form.html", {
        "active_page": "candidates",
        "page_title": "Manage Candidates",
        "form_title": "Edit Candidate",
        "form": form,
    })


@staff_member_required
@require_POST
def candidate_delete(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    candidate.delete()
    messages.success(request, "Candidate deleted.")
    return redirect("elections:manage_candidates")


@staff_member_required
def manage_voters(request):
    # The Add Voter popup posts back to this same page.
    form = VoterForm(request.POST or None)
    open_modal = False

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Voter added.")
            return redirect("elections:manage_voters")
        open_modal = True  # reopen the popup so the errors are visible

    voters = Voter.objects.all()
    q = request.GET.get("q", "").strip()
    department = request.GET.get("department", "")
    status = request.GET.get("status", "")
    if q:
        voters = voters.filter(
            Q(voter_id__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
        )
    if department:
        voters = voters.filter(department=department)
    if status:
        voters = voters.filter(status=status)

    return render(request, "OSAS/manage_voters.html", {
        "active_page": "voters",
        "page_title": "Manage Voters",
        "voters": voters,
        "q": q,
        "selected_department": department,
        "selected_status": status,
        "departments": Candidate.DEPARTMENT_CHOICES,
        "statuses": Voter.STATUS_CHOICES,
        "form": form,
        "open_modal": open_modal,
    })


@staff_member_required
def voter_edit(request, pk):
    voter = get_object_or_404(Voter, pk=pk)
    form = VoterForm(request.POST or None, instance=voter)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Voter updated.")
        return redirect("elections:manage_voters")

    return render(request, "OSAS/voter_form.html", {
        "active_page": "voters",
        "page_title": "Manage Voters",
        "voter": voter,
        "form": form,
    })


@staff_member_required
@require_POST
def voter_delete(request, pk):
    voter = get_object_or_404(Voter, pk=pk)
    voter.delete()
    messages.success(request, "Voter deleted.")
    return redirect("elections:manage_voters")


@staff_member_required
@require_POST
def voter_import(request):
    upload = request.FILES.get("file")
    if not upload:
        messages.error(request, "Please choose a CSV or Excel file first.")
        return redirect("elections:manage_voters")

    result = import_voters(upload)
    if result.fatal:
        messages.error(request, result.fatal)
        return redirect("elections:manage_voters")

    if result.created:
        messages.success(request, f"Imported {result.created} voter(s).")
    if result.skipped:
        messages.warning(request, f"Skipped {len(result.skipped)} row(s) with problems:")
        for row_number, reason in result.skipped[:10]:
            messages.error(request, f"Row {row_number}: {reason}")
        if len(result.skipped) > 10:
            messages.error(request, f"...and {len(result.skipped) - 10} more.")
    if not result.created and not result.skipped:
        messages.warning(request, "No voters were imported.")
    return redirect("elections:manage_voters")


@staff_member_required
def voter_import_template(request):
    """A ready-to-fill CSV that Excel opens correctly."""
    import csv

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="voters_template.csv"'
    response.write("\ufeff")  # BOM so Excel reads it as UTF-8
    writer = csv.writer(response)
    writer.writerow(TEMPLATE_HEADER)
    writer.writerows(TEMPLATE_ROWS)
    return response