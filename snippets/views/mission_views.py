from django.shortcuts import render
from snippets.models import Mission


def mission(request):

    missions = Mission.objects.all()[:3]

    return render(
        request,
        "snippets/mission.html",
        {"missions": missions}
    )
