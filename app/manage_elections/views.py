from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime
from .models import Election


def format_election_date(date):
    return timezone.localtime(date).strftime('%B %d, %Y | %I:%M %p')    # (2) local time


def serialize_election(election):
    start_local = timezone.localtime(election.start_date)                # (2) local time
    end_local = timezone.localtime(election.end_date)
    status = election.get_status()

    return {
        'id': election.id,
        'title': election.title,
        'description': election.description,
        'election_type': election.get_election_type_display(),
        'election_type_value': election.election_type,
        'department': election.department,
        'start_date': format_election_date(election.start_date),
        'end_date': format_election_date(election.end_date),
        # raw values used to pre-fill the Edit popup
        'start_date_raw': start_local.strftime('%Y-%m-%d'),
        'start_time_raw': start_local.strftime('%H:%M'),
        'end_date_raw': end_local.strftime('%Y-%m-%d'),
        'end_time_raw': end_local.strftime('%H:%M'),
        'status': status,
        'can_edit': str(status).lower() == 'upcoming',                   # Edit lang kapag Upcoming
    }


def error(message, field=None):
    payload = {'success': False, 'message': message}
    if field:
        payload['field'] = field                                         # para sa error sa ilalim ng field
    return JsonResponse(payload, status=400)


def read_election_form(request):
    """Validates the form. Returns (data, None) or (None, error_response)."""

    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()

    election_type = request.POST.get('election_type', '')
    department = request.POST.get('department', '')

    start_date_value = request.POST.get('start_date', '')
    start_time_value = request.POST.get('start_time', '')
    end_date_value = request.POST.get('end_date', '')
    end_time_value = request.POST.get('end_time', '')

    if not title:
        return None, error('Please enter an election title.', 'title')

    if election_type not in ["SSC", "CAMPUS", "DEPARTMENT"]:
        return None, error('Please select an election type.', 'election_type')

    if election_type == "DEPARTMENT":
        if department not in dict(Election.DEPARTMENT_CHOICES):
            return None, error('Please select a valid department.', 'department')
    else:
        department = ""

    if not all([start_date_value, start_time_value, end_date_value, end_time_value]):
        return None, error('Please complete all date and time fields.')

    try:
        start_date = datetime.strptime(
            start_date_value + ' ' + start_time_value, '%Y-%m-%d %H:%M'
        )
        end_date = datetime.strptime(
            end_date_value + ' ' + end_time_value, '%Y-%m-%d %H:%M'
        )
    except ValueError:
        return None, error('Invalid date or time.')

    if timezone.is_naive(start_date):
        start_date = timezone.make_aware(start_date)

    if timezone.is_naive(end_date):
        end_date = timezone.make_aware(end_date)

    # (3) bawal ang start date sa nakaraan
    if start_date < timezone.now().replace(second=0, microsecond=0):
        return None, error('Start date and time cannot be in the past.', 'start')

    if end_date <= start_date:
        return None, error('End date and time must be later than the start.', 'end')

    return {
        'title': title,
        'description': description,
        'election_type': election_type,
        'department': department,
        'start_date': start_date,
        'end_date': end_date,
    }, None


@staff_member_required(login_url='/accounts/login/')                     # (1) admin lang
def manage_elections(request):

    elections = Election.objects.all().order_by('-created_at')

    return render(request, 'OSAS/manage_elections.html', {
        'active_page': 'elections',                                       # (4) sidebar highlight
        'page_title': 'Manage Elections',
        'elections': [serialize_election(e) for e in elections],
    })


@staff_member_required(login_url='/accounts/login/')                     # (1)
@require_POST
def create_election(request):

    data, err = read_election_form(request)
    if err:
        return err

    election = Election.objects.create(**data)

    return JsonResponse({
        'success': True,
        'message': 'Election created successfully!',
        'election': serialize_election(election),
    })


@staff_member_required(login_url='/accounts/login/')                     # (1)
@require_POST
def edit_election(request, election_id):

    election = get_object_or_404(Election, id=election_id)

    # Upcoming lang ang pwedeng i-edit
    if str(election.get_status()).lower() != 'upcoming':
        return error('Only upcoming elections can be edited.')

    data, err = read_election_form(request)
    if err:
        return err

    for field, value in data.items():
        setattr(election, field, value)
    election.save()

    return JsonResponse({
        'success': True,
        'message': 'Election updated successfully!',
        'election': serialize_election(election),
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