from django.shortcuts import render
from django.contrib.auth.models import User


def ranking(request):

    users = User.objects.all().order_by("-profile__xp")[:10]

    return render(request, "snippets/ranking.html", {
        "users": users
    })