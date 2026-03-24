from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from snippets.models import AIChatHistory, Profile


@login_required
def ai_chat_history(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    histories_qs = AIChatHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    if profile.is_premium:
        histories = histories_qs
    else:
        histories = histories_qs[:3]

    return render(request, "snippets/ai_chat_history.html", {
        "histories": histories,
        "profile": profile,
    })