from django.shortcuts import render, redirect
from snippets.models import CommunityPost
from django.contrib.auth.decorators import login_required

@login_required
def community(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()

        if content:
            CommunityPost.objects.create(
                user=request.user,
                content=content
            )

        return redirect("community")

    posts = CommunityPost.objects.all().order_by("-created_at")

    return render(request, "snippets/community.html", {"posts": posts})