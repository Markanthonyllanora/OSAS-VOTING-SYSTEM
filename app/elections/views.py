from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CandidateForm
from .models import Candidate


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