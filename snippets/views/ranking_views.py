from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from snippets.models import Profile


@login_required
def ranking(request):

    # XPランキング
    users = Profile.objects.all().order_by("-xp", "-is_premium")[:50]

    all_users = Profile.objects.all().order_by("-xp")
    rank = list(all_users).index(request.user.profile) + 1

    return render(request, "snippets/ranking.html", {
        "users": users
    })