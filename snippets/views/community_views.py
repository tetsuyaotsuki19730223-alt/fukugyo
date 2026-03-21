from django.shortcuts import render, redirect, get_object_or_404
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
    post_count = posts.count()

    return render(request, "snippets/community.html", {
        "posts": posts,
        "post_count": post_count,
    })


@login_required
def edit_community_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, user=request.user)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()

        if content and content != post.content:
            post.content = content
            post.is_edited = True
            post.save()

        return redirect("community")

    return render(request, "snippets/edit_community_post.html", {
        "post": post,
    })


@login_required
def delete_community_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, user=request.user)

    if request.method == "POST":
        post.delete()

    return redirect("community")