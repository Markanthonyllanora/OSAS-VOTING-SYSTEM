from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime
from .models import Election


def format_election_date(date):
    return timezone.localtime(date).strftime('%B %d, %Y | %I:%M %p')    # (2) local time


@staff_member_required(login_url='/accounts/login/')                     # (1) admin lang
def manage_elections(request):

    elections = Election.objects.all().order_by('-created_at')

    election_data = []

    for election in elections:
        election_data.append({
            'id': election.id,
            'title': election.title,
            'description': election.description,
            'election_type': election.get_election_type_display(),
            'department': election.department,
            'start_date': format_election_date(election.start_date),
            'end_date': format_election_date(election.end_date),
            'status': election.get_status(),
        })

    return render(request, 'OSAS/manage_elections.html', {
        'active_page': 'elections',                                       # (4) sidebar highlight
        'page_title': 'Manage Elections',
        'elections': election_data
    })


@staff_member_required(login_url='/accounts/login/')                     # (1)
@require_POST
def create_election(request):

    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()

    election_type = request.POST.get('election_type', '')
    department = request.POST.get('department', '')

    start_date_value = request.POST.get('start_date', '')
    start_time_value = request.POST.get('start_time', '')

    end_date_value = request.POST.get('end_date', '')
    end_time_value = request.POST.get('end_time', '')

    if election_type not in ["SSC", "CAMPUS", "DEPARTMENT"]:
        return JsonResponse({
            'success': False,
            'message': 'Please select an election type.'
        }, status=400)

    if election_type == "DEPARTMENT":
        if department not in dict(Election.DEPARTMENT_CHOICES):
            return JsonResponse({
                'success': False,
                'message': 'Please select a valid department.'
            }, status=400)
    else:
        department = ""

    if not all([
        title,
        start_date_value,
        start_time_value,
        end_date_value,
        end_time_value
    ]):
        return JsonResponse({
            'success': False,
            'message': 'Please complete all required fields.'
        }, status=400)

    try:
        start_date = datetime.strptime(
            start_date_value + ' ' + start_time_value,
            '%Y-%m-%d %H:%M'
        )

        end_date = datetime.strptime(
            end_date_value + ' ' + end_time_value,
            '%Y-%m-%d %H:%M'
        )

    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid date or time.'
        }, status=400)



    if timezone.is_naive(start_date):
        start_date = timezone.make_aware(start_date)

    if timezone.is_naive(end_date):
        end_date = timezone.make_aware(end_date)

    # (3) bawal ang start date sa nakaraan
    if start_date < timezone.now().replace(second=0, microsecond=0):
        return JsonResponse({
            'success': False,
            'message': 'Start date and time cannot be in the past.'
        }, status=400)

    if end_date <= start_date:
        return JsonResponse({
            'success': False,
            'message': 'End date must be later than start date.'
        }, status=400)

    election = Election.objects.create(
        title=title,
        description=description,
        election_type=election_type,
        department=department,
        start_date=start_date,
        end_date=end_date
    )

    return JsonResponse({
        'success': True,
        'message': 'Election created successfully!',
        'election': {
            'id': election.id,
            'title': election.title,
            'description': election.description,
            'election_type': election.get_election_type_display(),
            'department': election.department,
            'start_date': format_election_date(election.start_date),
            'end_date': format_election_date(election.end_date),
            'status': election.get_status(),
        }
    })


@staff_member_required(login_url='/accounts/login/')                     # (1)
@require_POST
def delete_election(request, election_id):

    election = get_object_or_404(Election, id=election_id)
    election.delete()

    return JsonResponse({
        'success': True,
        'message': 'Election deleted successfully!'
    })