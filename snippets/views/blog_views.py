from django.shortcuts import render
from django.shortcuts import render
from snippets.models import BlogPost
from snippets.services.seo_service import generate_seo_article
from django.utils.text import slugify

def generate_blog(request):

    keyword = request.GET.get("keyword")

    content = generate_seo_article(keyword)

    post = BlogPost.objects.create(
        title=keyword,
        slug=slugify(keyword),
        content=content
    )

    return render(request, "snippets/blog_detail.html", {"post": post})

def blog_ai_sidejob(request):

    return render(
        request,
        "snippets/blog_ai_sidejob.html"
    )