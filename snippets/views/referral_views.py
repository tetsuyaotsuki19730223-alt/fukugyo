from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from snippets.models import Referral


@login_required
def referral_page(request):
        
    referral, created = Referral.objects.get_or_create(user=request.user)

    link = f"https://www.ai-sidejob-coach.net/signup/?ref={referral.code}"

    return render(
        request,
        "snippets/referral.html",
        {"link": link, "count": referral.invited_count}
    )