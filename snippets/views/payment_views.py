from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from snippets.models import Profile


def pricing(request):
    return render(request, "snippets/pricing.html")


@login_required
def checkout(request):
    return render(request, "snippets/checkout.html")


@login_required
def success(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.is_premium = True
    profile.save()

    return render(request, "snippets/success.html")