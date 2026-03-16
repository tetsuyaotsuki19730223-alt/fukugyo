from django.shortcuts import render


def simulator(request):

    income = None

    if request.method == "POST":

        hours = int(request.POST.get("hours", 1))
        skill = request.POST.get("skill")

        base = 1000

        if skill == "beginner":
            base = 1000

        elif skill == "normal":
            base = 2000

        elif skill == "pro":
            base = 4000

        income = hours * base * 30

    return render(
        request,
        "snippets/simulator.html",
        {"income": income}
    )