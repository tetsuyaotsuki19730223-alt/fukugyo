from django.shortcuts import render, redirect
from snippets.models import CommunityPost


def community(request):

    if request.method == "POST":

        content = request.POST.get("content")

        CommunityPost.objects.create(
            user=request.user,
            content=content
        )

        return redirect("community")

    posts = CommunityPost.objects.all().order_by("-created_at")

    return render(request, "snippets/community.html", {"posts": posts})
