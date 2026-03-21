from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from snippets.models import AIChatHistory


@login_required
def ai_chat_history(request):
    histories = AIChatHistory.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "snippets/ai_chat_history.html", {
        "histories": histories,
    })


@login_required
def ai_chat_history_detail(request, history_id):
    history = get_object_or_404(
        AIChatHistory,
        id=history_id,
        user=request.user
    )
    return render(request, "snippets/ai_chat_history_detail.html", {
        "history": history,
    })