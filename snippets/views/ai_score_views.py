from django.shortcuts import render
import random


def ai_sidejob_score(request):

    score = None

    if request.method == "POST":

        skill = request.POST.get("skill")
        time = request.POST.get("time")
        motivation = request.POST.get("motivation")

        base = 50

        if skill == "高い":
            base += 15

        if time == "3時間以上":
            base += 20

        if motivation == "高い":
            base += 15

        score = base + random.randint(-5, 5)

    return render(
        request,
        "snippets/ai_score.html",
        {"score": score}
    )