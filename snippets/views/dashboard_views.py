from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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


@login_required
def dashboard(request):

    return render(request, "snippets/dashboard.html")