from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.html import escape
from django.utils.safestring import mark_safe
from snippets.models import AIChatHistory, Profile


def highlight_text(text, keyword):
    escaped_text = escape(text)
    escaped_keyword = escape(keyword)

    if not keyword:
        return escaped_text

    highlighted = escaped_text.replace(
        escaped_keyword,
        f'<mark style="background: #fef08a; padding: 0 2px; border-radius: 4px;">{escaped_keyword}</mark>'
    )
    return mark_safe(highlighted)


@login_required
def ai_chat_history(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    q = request.GET.get("q", "").strip()

    all_histories = AIChatHistory.objects.filter(user=request.user)

    if q:
        all_histories = all_histories.filter(
            Q(question__icontains=q) | Q(answer__icontains=q)
        )

    all_histories = all_histories.order_by("-created_at")

    if profile.is_premium:
        paginator = Paginator(all_histories, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        histories = list(page_obj.object_list)
        is_limited = False
    else:
        histories = list(all_histories[:3])
        page_obj = None
        is_limited = all_histories.count() > 3

    for history in histories:
        history.highlighted_question = highlight_text(history.question, q)
        history.highlighted_answer = highlight_text(history.answer, q)

    return render(request, "snippets/ai_chat_history.html", {
        "histories": histories,
        "is_premium": profile.is_premium,
        "is_limited": is_limited,
        "q": q,
        "page_obj": page_obj,
    })


@login_required
def ai_chat_history_detail(request, history_id):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    history = get_object_or_404(
        AIChatHistory,
        id=history_id,
        user=request.user
    )

    if not profile.is_premium:
        allowed_ids = list(
            AIChatHistory.objects.filter(user=request.user)
            .order_by("-created_at")
            .values_list("id", flat=True)[:3]
        )
        if history.id not in allowed_ids:
            return render(request, "snippets/history_locked.html")

    return render(request, "snippets/ai_chat_history_detail.html", {
        "history": history,
    })


@login_required
def delete_ai_chat_history(request, history_id):
    history = get_object_or_404(
        AIChatHistory,
        id=history_id,
        user=request.user
    )

    if request.method == "POST":
        history.delete()

    return redirect("ai_chat_history")