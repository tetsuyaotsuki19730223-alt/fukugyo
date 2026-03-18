from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from snippets.models import Profile

@login_required
def dashboard(request):
    try:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return HttpResponse(
            f"OK user={request.user.username}, "
            f"xp={profile.xp}, level={profile.level}, streak={profile.streak}"
        )
    except Exception as e:
        return HttpResponse(f"ERROR: {e}")