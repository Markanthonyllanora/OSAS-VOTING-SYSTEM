from app.elections.models import Voter


def nav_user(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated or user.is_staff:
        return {}
    voter = Voter.objects.filter(voter_id__iexact=user.username).only("department").first()
    return {"nav_department": voter.department if voter else ""}