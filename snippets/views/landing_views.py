from django.shortcuts import render


def landing(request):
    return render(request, "snippets/landing.html")


def diagnosis_lp(request):
    return render(request, "snippets/diagnosis_lp.html")