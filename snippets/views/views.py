from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def success(request):

    token = request.GET.get("token")

    profile = request.user.profile

    if token and token == profile.payment_token:
        profile.is_premium = True
        profile.payment_token = ""  # 使い捨て
        profile.save()

    return render(request, "snippets/success.html")