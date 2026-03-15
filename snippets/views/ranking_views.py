from django.shortcuts import render


def ranking(request):

    ranking = [
        {"name": "taro", "xp": 120},
        {"name": "ken", "xp": 90},
        {"name": "yuki", "xp": 70},
    ]

    return render(
        request,
        "snippets/ranking.html",
        {"ranking": ranking}
    )
