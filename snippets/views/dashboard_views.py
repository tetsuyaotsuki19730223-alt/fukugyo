from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from snippets.models import Profile


def home(request):
    context = {
        "streak": 5,
        "xp": 120,
        "level": 2,
        "mission": "副業リサーチを10分する"
    }
    return render(request, "snippets/dashboard.html")

def landing(request):
    return render(request, "snippets/landing.html")


def dashboard(request):

    profile, _ = Profile.objects.get_or_create(user=request.user)

    xp = profile.xp or 0
    progress = xp % 100

    return render(request, "snippets/dashboard.html", {
        "progress": progress
    })

def to_int(value):
    try:
        return int(value)
    except:
        return 0
    
    value = to_int(request.POST.get("xxx"))